import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://attendance-system-1bc90-default-rtdb.firebaseio.com/"
})

ref = db.reference("Students")

# Python dictionary
data = {
    "TP011111":
    {
        "name": "Lee Wen Han",
        "major": "CS(AI)",
        "starting_year": 2021,
        "total_attendance": 20,
        "grades": "A",
        "year": 2,
        "last_attendance_taken": "2024-01-26 16:10:30",
    },

    "TP012345":
    {
        "name": "Wo Xing Shi",
        "major": "Badminton(China)",
        "starting_year": 2000,
        "total_attendance": 100,
        "grades": "S",
        "year": 1,
        "last_attendance_taken": "2024-01-26 17:10:30",
    },

    "TP054321":
    {
        "name": "David",
        "major": "Finance",
        "starting_year": 2019,
        "total_attendance": 97,
        "grades": "A",
        "year": 3,
        "last_attendance_taken": "2024-01-24 13:24:55",
    },

    "TP063338":
    {
        "name": "Elyse",
        "major": "Education",
        "starting_year": 1978,
        "total_attendance": 94,
        "grades": "A++",
        "year": 2,
        "last_attendance_taken": "2024-02-01 15:33:22",
    },

    "TP068713":
    {
        "name": "Wai Meng",
        "major": "Engineering",
        "starting_year": 1982,
        "total_attendance": 65,
        "grades": "B",
        "year": 1,
        "last_attendance_taken": "2023-06-13 09:31:16",
    },

    "TP088888":
    {
        "name": "Ah Wee",
        "major": "Business",
        "starting_year": 2013,
        "total_attendance": 87,
        "grades": "A+++",
        "year": 2,
        "last_attendance_taken": "2024-01-29 20:54:10",
    },
}

# Writing the dictionary details into the realtime database
for key, value in data.items():
    ref.child(key).set(value)
