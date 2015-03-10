for /f %%a in ('dir /b .\*.csv') do (

   mysql --user=root --password=spam5312 --database=pcsocalls --execute="LOAD DATA INFILE '.\\%%a' IGNORE INTO TABLE calls FIELDS TERMINATED BY ',';"

)

