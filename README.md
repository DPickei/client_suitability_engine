# LinkedIn Profile Analyzer

This tool processes LinkedIn profile data to extract and analyze key information. It's built to handle large datasets efficiently while maintaining data quality.

## What it does

- 
- Takes raw LinkedIn profile JSON data
- Cleans and organizes the data
- Uses Google's AI to analyze profile text
- Stores everything in a SQLite database for easy access

## Tech Stack

- Python 3.9+
- SQLite3
- AWS S3
- Gemini-2.0-flash ($0.10 / 1M output)

## Process

1. Send a request to Bright Data with a first and last name
2. Raw JSON files get processed into individual profiles
3. Desired attributes are gathered via directly copying or with Flash
4. Profiles are stored in db
5. CSV is created from db

## Why I built this

A client wishes to review many linkedin profiles but does not want to have to read through them manually. So this does that for them, and returns the profiles that seem to fit their search criteria best.

## How to set it up

1. Create a virtual environment
2. Install the dependencies
3. Set up your environment variables
4. Run the code

## License

MIT License

Copyright (c) 2024 David Pickei

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.