## Why I built this

A client wishes to review many linkedin profiles but does not want to have to read through them manually. So this does that for them, and returns the profiles that seem to fit their search criteria best.

## Process

1. Take a file for a name
2. Break it up into individual dictionaries for each person
    - one name will usually have multiple people associated
3. Add basic info to our database
4. Tag profiles that meet basic qualification criteria for nlp analysis
5. Process these profiles with nlp, store results
6. Tag profiles that meet our selection criteria
7. Export profiles to CSV

## How to set it up

- The project currently utilizes local dependencies and integrates with AWS S3 for data retrieval through BrightData's API. Current setup requires manual configuration of these components.

## Stack

- Python
    - Asyncio
- SQLite
- AWS S3
- Bright Data LinkedIn URL API
- Gemini-2.0-flash ($0.10 / 1M output)

## License

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

Copyright (c) 2024 David Pickei

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- NonCommercial — You may not use the material for commercial purposes.

Notices:
- You do not have to comply with the license for elements of the material in the public domain or where your use is permitted by an applicable exception or limitation.
- No warranties are given. The license may not give you all of the permissions necessary for your intended use. For example, other rights such as publicity, privacy, or moral rights may limit how you use the material.