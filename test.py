

while True:
    if not wleds: 
        time.sleep(1)
        continue

    for w in wleds:
        w.refresh()
    
    break

zeroconf.close()

tstring = LedString.strings['WLED-Test']
print(tstring.effects())
while True:
    tstring.update()
    time.sleep(0.2)
# headers ={'content-type':'application/json'}
# for i in range(25):
#     for j in range(25):
#         result = requests.post(f"http://{tstring.addr}/json/state", data=json.dumps(
#             {"seg":[{"fx": j+1, "pal": i+1}]}), headers=headers)
#         time.sleep(3)