# server.py
from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# --- Load Data ---
# Load the Excel file once when the server starts
try:
    df = pd.read_excel("lex.xlsx")
    print("Data loaded successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    df = pd.DataFrame() # Create empty DF to prevent crash

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lookup", methods=["POST"])
def lookup():
    # 1. Get input from the form
    country_input = request.form.get("country")
    year_input = request.form.get("year")
    
    # Clean the input (remove spaces, handle capitalization)
    # e.g., "  china  " -> "China"
    if country_input:
        country_clean = country_input.strip().title() 
    else:
        country_clean = ""

    result_msg = ""
    is_error = False

    # --- Error Handling Logic ---
    
    # Check 1: Did user input anything?
    if not country_clean or not year_input:
        result_msg = "Error: Please enter both a country name and a year."
        is_error = True
    
    else:
        # Check 2: Does the country exist in our data?
        # We match against the 'name' column
        matched_row = df[df['name'] == country_clean]

        if matched_row.empty:
            result_msg = f"Error: The country '{country_clean}' was not found in the dataset. Please check the spelling."
            is_error = True
        
        else:
            try:
                # Check 3: Validate Year
                year_int = int(year_input) # Try converting to integer
                
                # Check if year exists in the columns (header)
                if year_int in df.columns:
                    # Retrieve the value
                    life_expectancy = matched_row[year_int].values[0]
                    result_msg = f"The life expectancy in {country_clean} in {year_int} was {life_expectancy} years."
                else:
                    # Check 4: Year out of range
                    min_year = min([x for x in df.columns if isinstance(x, int)])
                    max_year = max([x for x in df.columns if isinstance(x, int)])
                    result_msg = f"Error: Data for the year {year_int} is not available. We only have data from {min_year} to {max_year}."
                    is_error = True

            except ValueError:
                # Check 5: Input is not a number
                result_msg = "Error: The year must be a number (e.g., 1990)."
                is_error = True

    # Return the result to the HTML page
    return render_template("analyze.html", 
                           result=result_msg, 
                           country=country_input, 
                           year=year_input,
                           is_error=is_error)

if __name__ == "__main__":
    app.run(debug=True)