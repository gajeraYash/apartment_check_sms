cd /home/gajerya/source/apartment_check_sms/
git pull origin main
source venv/bin/activate
python3 apartment_check.py $1
cp apartment_list.json apartment_list.json.bak
git add apartment_list.json apartment_list.json.bak
git commit -m "Updated JSON Tracking"
git push