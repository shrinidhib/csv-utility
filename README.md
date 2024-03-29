This project aims on enabling the user to perform custom manipulations on large CSV files. 
The framework employs parallel processing, by dividing the csv file into chunks and then processing them in a parallel fashion,
as well as layers of error detection for seamless user experience.

Input : 
1. Enter the csv file you wish to perform manipulation on.
2. A python file which performs the actual manipution on each row of data.

Process : 
The user can see the progress % while the manipulations are being performed.

Output : 
Consolidated edited output csv file is provided to the user. 


To run use the following commands : 

**for frontend**
`cd frontend`
`npm i`
`npm run start`

**for backend**
`cd backend`
`python3 server.py`
