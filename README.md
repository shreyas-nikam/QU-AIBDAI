# QU-NIST

## Set up steps

1. Clone the repository
2. Create a Virtual Environment: `python3 -m venv venv`
3. Activate the environment: `source venv/bin/activate`
4. Install the requirements: `pip install -r requirements.txt`
5. Create a `secrets.toml` file in `.streamlit` folder and add the keys as shown in the `secretes_example.toml`
6. Open terminal
7. Run `sudo -s`
8. Run `apt-get update`
9. Run `apt-get install libgl1` (and select Yes when prompted about using additional disk space for installations)
10. Exit from root.
11. Start Streamlit: `streamlit run main.py`

