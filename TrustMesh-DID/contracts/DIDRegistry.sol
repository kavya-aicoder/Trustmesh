// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title DIDRegistry
 * @notice Minimal on-chain registry for TrustMesh decentralized identities.
 *
 * Scope:
 * - DID creation
 * - DID resolution
 * - DID document reference
 * - Controller management
 * - Verification-key rotation
 * - Identity lifecycle (active / revoked)
 *
 * Security model:
 * - Private keys never enter the contract.
 * - The controller is the only account allowed to rotate keys, update the
 *   document reference, or change lifecycle state.
 * - DIDs are indexed by keccak256(DID string) to avoid storing duplicate IDs.
 *
 * Recovery-ready design:
 * - Controller authorization is isolated in `_onlyController` so a future
 *   guardian/recovery module can be introduced without changing DID storage.
 */
contract DIDRegistry {
    enum Status {
        None,
        Active,
        Revoked
    }

    struct DIDDocument {
        string documentReference;
        address controller;
        address verificationKey;
        uint256 createdAt;
        uint256 updatedAt;
        Status status;
    }

    mapping(bytes32 => DIDDocument) private _documents;

    event DIDCreated(
        bytes32 indexed didHash,
        string did,
        address indexed controller,
        address verificationKey,
        string documentReference
    );

    event DIDDocumentUpdated(
        bytes32 indexed didHash,
        string documentReference
    );

    event ControllerUpdated(
        bytes32 indexed didHash,
        address indexed previousController,
        address indexed newController
    );

    event KeyRotated(
        bytes32 indexed didHash,
        address indexed previousKey,
        address indexed newKey
    );

    event DIDRevoked(bytes32 indexed didHash, address indexed controller);

    error DIDAlreadyExists();
    error DIDNotFound();
    error InvalidDID();
    error InvalidController();
    error InvalidVerificationKey();
    error InvalidDocumentReference();
    error NotController();
    error DIDNotActive();
    error SameKey();
    error SameController();

    modifier onlyExisting(bytes32 didHash) {
        if (_documents[didHash].status == Status.None) revert DIDNotFound();
        _;
    }

    modifier onlyActive(bytes32 didHash) {
        if (_documents[didHash].status != Status.Active) revert DIDNotActive();
        _;
    }

    modifier onlyController(bytes32 didHash) {
        if (_documents[didHash].controller != msg.sender) revert NotController();
        _;
    }

    function createDID(
        string calldata did,
        string calldata documentReference,
        address verificationKey
    ) external returns (bytes32 didHash) {
        if (bytes(did).length == 0) revert InvalidDID();
        if (bytes(documentReference).length == 0) revert InvalidDocumentReference();
        if (msg.sender == address(0)) revert InvalidController();
        if (verificationKey == address(0)) revert InvalidVerificationKey();

        didHash = keccak256(bytes(did));
        if (_documents[didHash].status != Status.None) revert DIDAlreadyExists();

        uint256 timestamp = block.timestamp;
        _documents[didHash] = DIDDocument({
            documentReference: documentReference,
            controller: msg.sender,
            verificationKey: verificationKey,
            createdAt: timestamp,
            updatedAt: timestamp,
            status: Status.Active
        });

        emit DIDCreated(
            didHash,
            did,
            msg.sender,
            verificationKey,
            documentReference
        );
    }

    function resolveDID(string calldata did)
        external
        view
        returns (DIDDocument memory)
    {
        bytes32 didHash = _hashDID(did);
        if (_documents[didHash].status == Status.None) revert DIDNotFound();
        return _documents[didHash];
    }

    function getDIDHash(string calldata did) external pure returns (bytes32) {
        return _hashDID(did);
    }

    function updateDocumentReference(string calldata did, string calldata newReference)
        external
        onlyExisting(_hashDID(did))
        onlyActive(_hashDID(did))
        onlyController(_hashDID(did))
    {
        if (bytes(newReference).length == 0) revert InvalidDocumentReference();

        bytes32 didHash = _hashDID(did);
        _documents[didHash].documentReference = newReference;
        _documents[didHash].updatedAt = block.timestamp;

        emit DIDDocumentUpdated(didHash, newReference);
    }

    function rotateKey(string calldata did, address newVerificationKey)
        external
        onlyExisting(_hashDID(did))
        onlyActive(_hashDID(did))
        onlyController(_hashDID(did))
    {
        if (newVerificationKey == address(0)) revert InvalidVerificationKey();

        bytes32 didHash = _hashDID(did);
        address previousKey = _documents[didHash].verificationKey;
        if (previousKey == newVerificationKey) revert SameKey();

        _documents[didHash].verificationKey = newVerificationKey;
        _documents[didHash].updatedAt = block.timestamp;

        emit KeyRotated(didHash, previousKey, newVerificationKey);
    }

    function updateController(string calldata did, address newController)
        external
        onlyExisting(_hashDID(did))
        onlyActive(_hashDID(did))
        onlyController(_hashDID(did))
    {
        if (newController == address(0)) revert InvalidController();

        bytes32 didHash = _hashDID(did);
        address previousController = _documents[didHash].controller;
        if (previousController == newController) revert SameController();

        _documents[didHash].controller = newController;
        _documents[didHash].updatedAt = block.timestamp;

        emit ControllerUpdated(didHash, previousController, newController);
    }

    function revokeDID(string calldata did)
        external
        onlyExisting(_hashDID(did))
        onlyActive(_hashDID(did))
        onlyController(_hashDID(did))
    {
        bytes32 didHash = _hashDID(did);
        _documents[didHash].status = Status.Revoked;
        _documents[didHash].updatedAt = block.timestamp;

        emit DIDRevoked(didHash, msg.sender);
    }

    function isActive(string calldata did) external view returns (bool) {
        return _documents[_hashDID(did)].status == Status.Active;
    }

    function _hashDID(string calldata did) private pure returns (bytes32) {
        if (bytes(did).length == 0) revert InvalidDID();
        return keccak256(bytes(did));
    }
}
