=============SETUP=============
1. Login: 
ssh: root@50.116.49.177   Password: TowerPower$73
ssh2: njit@60.116.48.177  Password: temppass

2. Navitate to path:
    cd root/home/njit/dev/Albama-PSWS/

3. Activate vitrual environment: 
    . venv/bin/activate

4. Run server:
    cd PSWS/
    ./manage.py runserver 0:8000

5. Run ngrok:
    in new terminal, navitate to path njit/dev/, run: ./ngrok http 8000 
    then open the link in browser

6. Kill existing server (and run 4 and 5 if need):
    kill 8000
    sudo fuser -k 8000/tcp
    kill -9 "$(pgrep ngrok)"

7. Test website in the browser:
    test account: root  pw: super
    check database: (website address from step 5)/admin


===============CODE================
The basic idea of making the website is doing frontend in analysis_map.html and pass information from form to the backend in views.py
1. analysis_map.html includes:
    1.1: frontend display
    1.2: javascript functions doing global map plot; select/unselect clickbox; lineplot display; get_info for infomation if needed
    1.3: after sending a request, the backend will send back a data which will be parsed to display in frontend. 
2. views.py includes:
    2.1: station_analysis(request, id=None) and updateStatus() for getting station data from database
    2.1: analysis_map(request) function to parse information from frontend, request data from database, parse it, and pass it back to frontend for display
