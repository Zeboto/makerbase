# Makerbase
### Installation:
1. Install requirements (Raspberry Pi)

    ```sh
    pip install -r requirements.txt
    ```
2. Start MongoDB server
    
    ```sh
    docker run -d -p 27017:27017 -v ~/data:/data/db --name mongo mongo:bionic
    ```
3. Rename `config.example.toml` to `config.toml` (and applying changes if needed)
### Running:

Run through VSCode default flask configuration with `sudo: true` or 
```sh
sudo -E /bin/python3 -m flask run
```