import { network } from "hardhat";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const { ethers } = await network.create();

const [deployer] = await ethers.getSigners();

console.log("========================================");
console.log("TrustMesh Local Deployment");
console.log("========================================");
console.log("Deployer:", deployer.address);

const networkInfo = await ethers.provider.getNetwork();

console.log("Chain ID:", networkInfo.chainId.toString());

if (networkInfo.chainId !== 31337n) {
  throw new Error(
    `Wrong network. Expected local Hardhat network (31337), got ${networkInfo.chainId}`
  );
}

const balance = await ethers.provider.getBalance(
  deployer.address
);

console.log(
  "Deployer balance:",
  ethers.formatEther(balance),
  "ETH"
);

if (balance === 0n) {
  throw new Error(
    "Deployer wallet has no ETH."
  );
}

console.log("\n[1/4] Deploying DIDRegistry...");

const didRegistry =
  await ethers.deployContract("DIDRegistry", {
    gasLimit: 2750000,
  });

await didRegistry.waitForDeployment();

const didRegistryAddress =
  await didRegistry.getAddress();

console.log(
  "DIDRegistry:",
  didRegistryAddress
);

console.log("\n[2/4] Deploying PolicyEngine...");

const policyEngine =
  await ethers.deployContract(
    "PolicyEngine",
    [deployer.address]
  );

await policyEngine.waitForDeployment();

const policyEngineAddress =
  await policyEngine.getAddress();

console.log(
  "PolicyEngine:",
  policyEngineAddress
);

console.log("\n[3/4] Deploying AuditLogger...");

const auditLogger =
  await ethers.deployContract(
    "AuditLogger",
    [deployer.address]
  );

await auditLogger.waitForDeployment();

const auditLoggerAddress =
  await auditLogger.getAddress();

console.log(
  "AuditLogger:",
  auditLoggerAddress
);

console.log("\n[4/4] Deploying AssetNFT...");

const assetNFT =
  await ethers.deployContract(
    "AssetNFT",
    [
      policyEngineAddress,
      didRegistryAddress,
      auditLoggerAddress,
    ]
  );

await assetNFT.waitForDeployment();

const assetNFTAddress =
  await assetNFT.getAddress();

console.log(
  "AssetNFT:",
  assetNFTAddress
);

console.log(
  "\nAuthorizing AssetNFT as an AuditLogger emitter..."
);

const emitterTx =
  await auditLogger.setEmitterAuthorized(
    assetNFTAddress,
    true
  );

await emitterTx.wait();

console.log(
  "AssetNFT audit emitter authorization confirmed."
);

const deployment = {
  network: "hardhatLocal",
  chainId: Number(networkInfo.chainId),
  deployer: deployer.address,
  contracts: {
    DIDRegistry: didRegistryAddress,
    PolicyEngine: policyEngineAddress,
    AuditLogger: auditLoggerAddress,
    AssetNFT: assetNFTAddress,
  },
  deployedAt: new Date().toISOString(),
};

const deploymentDir = path.resolve(
  "deployment"
);

const abiDir = path.resolve(
  "deployment",
  "abi"
);

await mkdir(abiDir, {
  recursive: true,
});

await writeFile(
  path.join(
    deploymentDir,
    "addresses.json"
  ),
  JSON.stringify(
    deployment,
    null,
    2
  ) + "\n",
  "utf8"
);

const contracts = [
  "DIDRegistry",
  "PolicyEngine",
  "AuditLogger",
  "AssetNFT",
];

for (const contractName of contracts) {
  const contractFactory =
    await ethers.getContractFactory(
      contractName
    );

  await writeFile(
    path.join(
      abiDir,
      `${contractName}.json`
    ),
    JSON.stringify(
      {
        contractName,
        abi: JSON.parse(
          contractFactory.interface.formatJson()
        ),
      },
      null,
      2
    ) + "\n",
    "utf8"
  );
}

console.log("\n========================================");
console.log("Deployment complete");
console.log("========================================");

console.log(
  "\nDeployment addresses saved to:"
);

console.log(
  "deployment/addresses.json"
);

console.log(
  "\nABIs saved to:"
);

console.log(
  "deployment/abi/"
);

console.log("\nContract addresses:");

console.log(
  "DIDRegistry:",
  didRegistryAddress
);

console.log(
  "PolicyEngine:",
  policyEngineAddress
);

console.log(
  "AuditLogger:",
  auditLoggerAddress
);

console.log(
  "AssetNFT:",
  assetNFTAddress
);