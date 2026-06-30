from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import ArtisanProfile, CustomerProfile, Speciality
from django.contrib.auth import get_user_model

User = get_user_model()

SPECIALITY_MAP = {
    "1": "plumber",    "2": "electrician",
    "3": "carpenter",  "4": "tailor",
    "5": "barber",     "6": "hairstylist",
    "7": "makeup_artist"
}

SPECIALITY_MENU = (
    "1. Plumber\n2. Electrician\n3. Carpenter\n4. Tailor\n"
    "5. Barber\n6. Hairstylist\n7. Makeup Artist"
)


def get_or_none(phone_number):
    return User.objects.filter(phone_number=phone_number).first()


@csrf_exempt
def ussd_handler(request):
    phone_number = request.POST.get('phoneNumber', '')
    text         = request.POST.get('text', '')
    user_input   = text.split('*') if text else []
    depth        = len(user_input)

    response = ""

    # ── MAIN MENU ──
    if text == "":
        response = (
            "CON Welcome to HustleLink\n"
            "1. Find Artisan\n"
            "2. Register as an Artisan"
        )

    # ══════════════════════════════════════
    # FLOW 1 — FIND ARTISAN
    # name → city → state → country → skill (1 only) → MATCH
    # ══════════════════════════════════════

    elif user_input[0] == "1" and depth == 1:
        response = "CON Enter your full name:"

    elif user_input[0] == "1" and depth == 2:
        response = "CON Enter your city:"

    elif user_input[0] == "1" and depth == 3:
        response = "CON Enter your state:"

    elif user_input[0] == "1" and depth == 4:
        response = "CON Enter your country:"

    elif user_input[0] == "1" and depth == 5:
        response = f"CON Choose the skill you need:\n{SPECIALITY_MENU}"

    elif user_input[0] == "1" and depth == 6:
        name     = user_input[1]
        city     = user_input[2]
        state    = user_input[3]
        country  = user_input[4]
        skill_choice = user_input[5]
        speciality   = SPECIALITY_MAP.get(skill_choice)

        if not speciality:
            response = "END Invalid choice. Please try again."
        else:
            # Save/update this person as a customer (phone number identifies them)
            user = get_or_none(phone_number)
            if not user:
                user = User.objects.create_user(
                    phone_number=phone_number,
                    name=name,
                    is_customer=True,
                )
            else:
                user.is_customer = True
                user.save()

            if not hasattr(user, 'customer_profile'):
                CustomerProfile.objects.create(
                    customer=user, city=city, state=state, country=country
                )

            # Find matching artisans in same state + country, with that skill
            artisans = ArtisanProfile.objects.filter(
                state=state,
                country=country,
                specialities__name=speciality,
                artisan__is_active=True
            ).distinct()[:5]

            if artisans:
                menu = "END Artisans near you:\n"
                for a in artisans:
                    menu += f"{a.artisan.name} - {a.artisan.phone_number}\n"
                response = menu
            else:
                response = "END No artisans available for that skill in your area yet."

    # ══════════════════════════════════════
    # FLOW 2 — REGISTER AS ARTISAN
    # skill(s) → name → city → state → country → done
    # ══════════════════════════════════════

    elif user_input[0] == "2" and depth == 1:
        user = get_or_none(phone_number)
        if user and user.is_artisan:
            response = "END You are already registered as an artisan on HustleLink."
        else:
            response = f"CON Choose skill(s), separate by comma e.g 1,3,5:\n{SPECIALITY_MENU}"

    elif user_input[0] == "2" and depth == 2:
        response = "CON Enter your full name:"

    elif user_input[0] == "2" and depth == 3:
        response = "CON Enter your city:"

    elif user_input[0] == "2" and depth == 4:
        response = "CON Enter your state:"

    elif user_input[0] == "2" and depth == 5:
        response = "CON Enter your country:"

    elif user_input[0] == "2" and depth == 6:
        skill_choices = user_input[1].split(',')   # e.g. "1,3,5" → ["1","3","5"]
        name    = user_input[2]
        city    = user_input[3]
        state   = user_input[4]
        country = user_input[5]

        specialities = [SPECIALITY_MAP.get(c.strip()) for c in skill_choices]
        specialities = [s for s in specialities if s]  # remove invalid entries

        if not specialities:
            response = "END Invalid skill choice. Please try again."
        else:
            user = get_or_none(phone_number)

            if not user:
                user = User.objects.create_user(
                    phone_number=phone_number,
                    name=name,
                    is_artisan=True,
                )
            else:
                user.is_artisan = True
                user.save()

            if not hasattr(user, 'artisan_profile'):
                profile = ArtisanProfile.objects.create(
                    artisan=user, city=city, state=state, country=country
                )
                # Attach each chosen speciality
                for s in specialities:
                    speciality_obj, _ = Speciality.objects.get_or_create(name=s)
                    profile.specialities.add(speciality_obj)

                response = "END Registered! You will receive an SMS when a job is available."
            else:
                response = "END This number is already registered as an artisan."

    else:
        response = "END Something went wrong. Please try again."

    return HttpResponse(response, content_type="text/plain")