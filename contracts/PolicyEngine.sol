// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/// @title PolicyEngine
/// @notice Generic on-chain RBAC engine for TrustMesh.
/// @dev Organizations define their own roles, resources, actions and policies.
///      Roles such as Admin/Manager/User are NOT hard-coded.
contract PolicyEngine is Ownable {
    struct Role {
        bool exists;
        string name;
    }

    mapping(bytes32 => Role) private _roles;

    // User/identity wallet => assigned role
    mapping(address => bytes32) private _userRoles;

    // Role => Resource => Action => permission
    mapping(bytes32 => mapping(bytes32 => mapping(bytes32 => bool)))
        private _permissions;

    event RoleCreated(
        bytes32 indexed roleId,
        string name
    );

    event RoleAssigned(
        address indexed subject,
        bytes32 indexed roleId
    );

    event RoleRevoked(
        address indexed subject,
        bytes32 indexed roleId
    );

    event PermissionConfigured(
        bytes32 indexed roleId,
        bytes32 indexed resourceId,
        bytes32 indexed actionId,
        bool allowed
    );

    event AccessGranted(
        address indexed subject,
        bytes32 indexed roleId,
        bytes32 indexed resourceId,
        bytes32 actionId
    );

    event AccessDenied(
        address indexed subject,
        bytes32 indexed roleId,
        bytes32 indexed resourceId,
        bytes32 actionId
    );

    error EmptyRoleName();
    error InvalidRole();
    error RoleAlreadyExists();
    error InvalidSubject();
    error RoleNotAssigned();

    constructor() Ownable(msg.sender) {}

    /// @notice Organization creates a custom role.
    function createRole(
        bytes32 roleId,
        string calldata name
    ) external onlyOwner {
        if (roleId == bytes32(0)) {
            revert InvalidRole();
        }

        if (bytes(name).length == 0) {
            revert EmptyRoleName();
        }

        if (_roles[roleId].exists) {
            revert RoleAlreadyExists();
        }

        _roles[roleId] = Role({
            exists: true,
            name: name
        });

        emit RoleCreated(roleId, name);
    }

    /// @notice Assign an existing role to an identity.
    function assignRole(
        address subject,
        bytes32 roleId
    ) external onlyOwner {
        if (subject == address(0)) {
            revert InvalidSubject();
        }

        if (!_roles[roleId].exists) {
            revert InvalidRole();
        }

        _userRoles[subject] = roleId;

        emit RoleAssigned(subject, roleId);
    }

    /// @notice Remove a user's assigned role.
    function revokeRole(
        address subject
    ) external onlyOwner {
        if (subject == address(0)) {
            revert InvalidSubject();
        }

        bytes32 roleId = _userRoles[subject];

        if (roleId == bytes32(0)) {
            revert RoleNotAssigned();
        }

        delete _userRoles[subject];

        emit RoleRevoked(subject, roleId);
    }

    /// @notice Configure whether a role can perform an action on a resource.
    function setPermission(
        bytes32 roleId,
        bytes32 resourceId,
        bytes32 actionId,
        bool allowed
    ) external onlyOwner {
        if (!_roles[roleId].exists) {
            revert InvalidRole();
        }

        if (
            resourceId == bytes32(0) ||
            actionId == bytes32(0)
        ) {
            revert InvalidRole();
        }

        _permissions[roleId][resourceId][actionId] = allowed;

        emit PermissionConfigured(
            roleId,
            resourceId,
            actionId,
            allowed
        );
    }

    /// @notice Evaluate access and record the decision on-chain.
    function checkAccess(
        address subject,
        bytes32 resourceId,
        bytes32 actionId
    ) external returns (bool allowed) {
        bytes32 roleId = _userRoles[subject];

        allowed =
            subject != address(0) &&
            roleId != bytes32(0) &&
            resourceId != bytes32(0) &&
            actionId != bytes32(0) &&
            _permissions[roleId][resourceId][actionId];

        if (allowed) {
            emit AccessGranted(
                subject,
                roleId,
                resourceId,
                actionId
            );
        } else {
            emit AccessDenied(
                subject,
                roleId,
                resourceId,
                actionId
            );
        }
    }

    /// @notice Get a user's assigned role.
    function getUserRole(
        address subject
    ) external view returns (bytes32) {
        return _userRoles[subject];
    }

    /// @notice Get role information.
    function getRole(
        bytes32 roleId
    )
        external
        view
        returns (
            bool exists,
            string memory name
        )
    {
        Role memory role = _roles[roleId];

        return (
            role.exists,
            role.name
        );
    }

    /// @notice Read-only permission check for frontend/backend.
    function hasPermission(
        address subject,
        bytes32 resourceId,
        bytes32 actionId
    ) external view returns (bool) {
        bytes32 roleId = _userRoles[subject];

        return
            subject != address(0) &&
            roleId != bytes32(0) &&
            resourceId != bytes32(0) &&
            actionId != bytes32(0) &&
            _permissions[roleId][resourceId][actionId];
    }
}