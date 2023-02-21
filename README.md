# Legitimate_Interest_Crawler
We created a web crawler to analyze 10,000 websites privacy notices from the Tranco top sites list4 which provides
rankings that are oriented for research, and aims to be reproducible.


# Setting up the repo
1. Clone this repository in the remote machine
2. To use this code, you will need to have Python 3 installed on your machine.
  You can download it from the official [Python website.](https://www.python.org/downloads/)
3. Navigate to the Code Directory
   * 'cd codes'
4. Create a new environment:
    - can be done with conda or virtualenv
5. Activate the new environment and install the requirements:
    - activate the environment
   * `pip install -r requirements.txt`
6. You should now be able to run the code as follows:
   * `python crawler.py` 
   

Results
The code will output a table with the following information for each website in the input file:
    [Rank
    Website URL
    Number of pages with legitimate interests
    Whether there are any legitimate interests on the website
    Number of clicks needed to find legitimate interests (if any)
    Error (if any)]
The code will also output a CSV file with the list of websites and their legitimate  purposes(in terms od True or False).

Additionally, Screenshots and text data are saved in output_files/


If you would like to contribute to this project, please open an issue or submit a pull request on GitHub.
