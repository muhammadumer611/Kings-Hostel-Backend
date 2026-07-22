from app.firebase.firebase import db


class StudentIDGenerator:

    def generate(self):

        counter_ref = db.collection("counters").document("students")

        counter = counter_ref.get()

        if counter.exists:

            current = counter.to_dict()["value"] + 1

        else:

            current = 1

        counter_ref.set(
            {
                "value": current
            }
        )

        return f"STU-{current:04d}"