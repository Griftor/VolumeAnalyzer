:: A batch file to automate the process to generate folders to hold the tick data, along with a copy of the plotter script
@echo off
:: Parameters - Symbol, Database, Start Date, End Date, Header Line, Units
bash -c "./tick.sh %1 %2 %3 %4 %1.csv"

python OneTickToLSS.py %1.csv %5 %6

echo done