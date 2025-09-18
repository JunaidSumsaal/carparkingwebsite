from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
import cv2, json, numpy as np
from ultralytics import YOLO
from .models import DetectionResult, FAQ, UserFeedback, ContactMessage
from django.contrib import messages
from .models import Registration
import re
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

# Paths
VIDEO_PATH = "parking1.mp4"
YOLO_MODEL_PATH = "yolo11s.pt"
JSON_FILE = "bounding_boxes.json"
TARGET_CLASSES = [2]  # only cars

# Load model + polygons once
model = YOLO(YOLO_MODEL_PATH)
with open(JSON_FILE) as f:
    polygons = json.load(f)



def signup(request):
    if request.method == "POST":
        username = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # email already exists
        if Registration.objects.filter(email=email).exists():
            messages.error(request, "Email already used!")
            return render(request, "signup.html")

        # strong password validation
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "signup.html")

        if not re.search(r"[A-Z]", password):
            messages.error(request, "Password must contain at least one uppercase letter.")
            return render(request, "signup.html")

        if not re.search(r"[a-z]", password):
            messages.error(request, "Password must contain at least one lowercase letter.")
            return render(request, "signup.html")

        if not re.search(r"\d", password):
            messages.error(request, "Password must contain at least one digit.")
            return render(request, "signup.html")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            messages.error(request, "Password must contain at least one special character (!@#$ etc).")
            return render(request, "signup.html")

        # Save user
        user = Registration(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "signup.html")



def login(request):
    if request.method == "POST":
        email = request.POST.get("email")  # from your <input name="name">
        password = request.POST.get("password")

        try:
            user = Registration.objects.get(email=email, password=password)
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            return redirect("home")  

        except Registration.DoesNotExist:
            messages.error(request, "Invalid email or password")
    return render(request, 'login.html')






def home(request):
    # show last 5 saved results (optional)
    results = DetectionResult.objects.all().order_by("-timestamp")[:5]
    return render(request, "home.html", {"results": results})


def gen_frames():
    cap = cv2.VideoCapture(VIDEO_PATH)

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_resized = cv2.resize(frame, (1080, 600))
        results = model(frame_resized)[0]

        # Collect detected car boxes
        boxes = []
        for box, cls in zip(results.boxes.xyxy.cpu().numpy(), results.boxes.cls.cpu().numpy()):
            if int(cls) in TARGET_CLASSES:
                boxes.append(box)

        # Check each parking slot
        occupied_flags = []
        for poly in polygons:
            pts = np.array(poly["points"], dtype=np.int32).reshape((-1, 1, 2))
            occupied = False
            for box in boxes:
                xc = int((box[0] + box[2]) / 2)
                yc = int((box[1] + box[3]) / 2)
                if cv2.pointPolygonTest(pts, (xc, yc), False) >= 0:
                    occupied = True
                    break
            occupied_flags.append(occupied)

            # Draw polygons + status
            color = (0, 0, 255) if occupied else (0, 255, 0)
            status_text = "Occupied" if occupied else "Available"
            cv2.polylines(frame_resized, [pts], True, color, 2)
            cv2.putText(frame_resized, status_text, tuple(pts[0][0]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        occupied = sum(occupied_flags)
        available = len(occupied_flags) - occupied

        # Save snapshot in DB (latest state)
        DetectionResult.objects.create(
            timestamp=timezone.now(),
            occupied=occupied,
            available=available
        )

        # Encode frame for streaming
        ret, buffer = cv2.imencode('.jpg', frame_resized)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


def video_feed(request):
    return StreamingHttpResponse(gen_frames(),
                                 content_type="multipart/x-mixed-replace; boundary=frame")


#  New: JSON endpoint for live counts
def latest_counts(request):
    result = DetectionResult.objects.order_by("-timestamp").first()
    if result:
        return JsonResponse({
            "occupied": result.occupied,
            "available": result.available,
            "timestamp": result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    else:
        return JsonResponse({"occupied": 0, "available": 0, "timestamp": ""})




# If your contact page is rendering from template:
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        # redirect to thank you page or same page with success message
        return render(request, 'contact.html', {'success': True})

    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')

def faq(request):
    faqs = FAQ.objects.all()  # All FAQ entries
    return render(request, 'faq.html', {'faqs': faqs})

def history(request):
    results = DetectionResult.objects.order_by('-timestamp')[:100]
    return render(request, 'history.html', {'results': results})

def feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        UserFeedback.objects.create(name=name, email=email, message=message)
        messages.success(request, 'Thank you for your feedback!')
        return redirect('feedback') 

    feedbacks = UserFeedback.objects.all()[:10]  
    return render(request, 'userfeedback.html', {'feedbacks': feedbacks})


def logout_view(request):
    """Logs out the user and redirects to login."""
    auth_logout(request)  # use the imported alias
    return redirect('login')  # or wherever you want
