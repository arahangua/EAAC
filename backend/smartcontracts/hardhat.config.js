require('dotenv').config();  // This line should be at the top of your file
require("@nomicfoundation/hardhat-toolbox");
require('@openzeppelin/hardhat-upgrades');

const { PRIVATE_KEY } = process.env;

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.20",
  networks: {
    sepolia: {
      url: "https://eth-sepolia.g.alchemy.com/v2/BXTIlJtbnnui83o2tieUz2HCJkTO5iPp",
      accounts: [`0x${process.env.PRIVATE_KEY}`]
    }
  }
};
