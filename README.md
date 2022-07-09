# Web3 Graveyard

**Web3 Graveyard** contains analysis and PoCs for past exploits.

# Setup

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
