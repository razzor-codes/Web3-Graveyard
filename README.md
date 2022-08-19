# Web3 Graveyard

[Web3 Graveyard](https://web3graveyard.ml) is a database of past Web3 hacks

### Gravedigger

**gravedigger** is a helper utility to query database for specific information and also update it with new hacks

### Install

`pip3 install -e .` from the root of this directory. It will install the tool in edit mode (create symlinks), means you can edit the code and changes will be reflected directly to your environment.

### Usage

`auth` : Sets up the github authentication token

```
gravedigger auth GithubAuthToken
```

`find` : Reverse Search an attacker address which was involved with a particular project  

```
gravedigger find 0xa0c7BD318D69424603CBf91e9969870F21B8ab4c 
```

`range` : Find hacks which happened within a given date range

```
gravedigger range -s "1 August 2022" -e "7 August 2022"
```

`s` and `e` are optional parameters, if not provided will pick the default values

`update` : Update the database with new hacks

```
gravedigger update audius
```

### Tips
* Date provided, either for finding hacks within a range or updating the database should follow the strict format as %d Month %Y (1 June 2022)
* While updating new hacks the input addresses are supposed to be block explorer links like 
`https://etherscan.io/address/0xA62c3ced6906B188A4d4A3c981B79f2AABf2107F`
---

### PoCs/Analysis

The repo also contains some analysis and PoCs for past exploits.

### Setup

### Install Dependencies
```bash
npm install
```

### Add API and Private Keys  
Add your node api keys in the `.env` file

### Modify Block Number
All the tests fork respective chains at a certain block number. Modify them as per the needs.

### Run PoC Tests
All the tests are organized in their respective protocol/project's folder.  
```bash
npx hardhat test .\test\<project_name>\<test>
```

### Exploit Analysis
The detailed analysis for every exploit can be found in the `README.md` file in every `\contracts\<project_name>\` directory.
