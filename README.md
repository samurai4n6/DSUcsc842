# DSUcsc842
Code for DSU CSC 842 course


Cycle2 - Zendesk Ticket Collection

What is the purpose of the project?

The purpose of the project came from a need that I have in collecting metrics for cyber security tickets that our SOC performs.
Management was asking how many tickets our SOC was receiving to be worked, which aided in showing how many more positions we needed for hire.

The Zendesk API is required, and hte following link is beneficial:
https://developer.zendesk.com/api-reference/

Why is project the useful?

This project is use for cyber security management. I need to understand how many tickets we receive to gauge work load, identify trends and increases in work, and effectively
manage work in our SOC.

What does the project do?

This project does the following:
-Identifies an initial and end dates that pertain to the timeframe you would like cyber security tickets to be collected.
-Checks and cleans up JSON and CSV files that may be present from a previous run.
-Builds an HTTPS connection to the Zendesk API to pull ticket related data in JSON format within the requested time frame.
-Creates a JSON file of the ticket data.
-Creates a CSV with targeted fields/keys from the JSON data.
-Utilizes pandas to count tickets by date and generating a line graph of the count by data.

Future Work

-Integrate more API calls to further enrich the ticket data for metrics.
-Perform additional statistical analysis via pandas for metrics.

Cycle4 -

Cycle6 - 

Cycle8 - 

Cycle10 -
