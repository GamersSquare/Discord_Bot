import aladhan
location = aladhan.City("Cairo", "EG")  # Doha, Qatar
client = aladhan.Client(location)
adhans = client.get_today_times()
for adhan in adhans:
    print(adhan.readable_timing(show_date=False))

# import datetime
#
# time = datetime.datetime.now().strftime("%H:%M (%p)")
# print(time)

# from playsound import playsound
#
# playsound("الأذان المكي.mp3")
