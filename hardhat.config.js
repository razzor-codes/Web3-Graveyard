//const { hardhatArguments } = require('hardhat');

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
require('dotenv').config();
require("@nomiclabs/hardhat-waffle")
require("@nomiclabs/hardhat-etherscan")
require("@openzeppelin/hardhat-upgrades")
require("@nomiclabs/hardhat-ethers")


task("accounts", "Prints the list of accounts", async (taskArgs, hre) => {
  const accounts = await hre.ethers.getSigners();
  
  for (const account of accounts) {
    console.log(account.address);
  }
});



module.exports = {
  solidity: {
    compilers: [
      {
        version: "0.8.13",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          }
        }
      },
      {
        version: "0.5.16"
      },
      {
        version: "0.6.12"
      }

    ],
  },
  mocha: {
    timeout: 10000000000
  },
  networks: {
    hardhat: {
      accounts: {
        accountsBalance: '5000000000000000000000000000000'
      },
    allowUnlimitedContractSize: true,
    forking: {
        // url: process.env.ALCHEMY_OPTIMISM,
        // blockNumber: 15057989,
        // enabled: false
      }
    },
  }
};
