## Employment verification system using web scrapping of EPFO Website

Base URL : <a href="https://unifiedportal-epfo.epfindia.gov.in/publicPortal/no-auth/misReport/home/loadEstSearchHome/">EPFO Home Page</a>

## Please Find for reference
* Installation and Run the code
* File Structure
* Tech Stack
* Further Improvements
* Timeline

## Installation
1. Clone the repository
```sh
git clone https://github.com/KrutikaBhatt/Employment_verification_system
```
    
3. Create a virtual environment
    ```sh
    virtualenv env
    env\Scripts\activate
    ```
    
4. Install the requirements
    ```sh
    pip install -m requirements.txt
    ```
5. Run the Code
    ```sh
    python main.py
    ```

##  File Structure
1. Find the captcha decoding algorithm in <a href="https://github.com/KrutikaBhatt/Employment_verification_system/tree/master/captcha_detection">captcha_detection</a>
2. Find the I/O handling or prompt handling code file in <a href="https://github.com/KrutikaBhatt/Employment_verification_system/tree/master/prompts">prompts folder</a>
3. The web scrapping functions and modules are written in <a href="https://github.com/KrutikaBhatt/Employment_verification_system/blob/master/scraper.py">scrapper.py</a>
4. The main.py file is the driver file
