const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const captureButton = document.getElementById('Capture');
const description = document.getElementById('Description');
const title = document.querySelector('.centered-text p');

let webcamStarted = false;

startButton.addEventListener('click', startWebcam);
stopButton.addEventListener('click', stopWebcam);

function startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
            video.play();
            startButton.style.display = 'none';
            stopButton.style.display = 'block';
            captureButton.style.display = 'block';
            title.style.display = 'none';
            description.style.display = 'none';
            video.style.border = '5px solid black';
            video.style.borderRadius = '5px';
            webcamStarted = true;
        })
        .catch((error) => {
            console.error('Error accessing webcam:', error);
        });
}

function stopWebcam() {
    const tracks = video.srcObject.getTracks();
    tracks.forEach(track => track.stop());
    video.srcObject = null;
    startButton.style.display = 'block';
    stopButton.style.display = 'none';
    captureButton.style.display = 'none';
    title.style.display = 'block';
    description.style.display = 'block';
    video.style.border = 'none';
    video.style.borderRadius = 'none';
    webcamStarted = false;
}

function captureImage() {
    alert("picture taken")
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageDataUrl = canvas.toDataURL('image/png');
    $.ajax({
        type: "POST",
        url: "/recognition",
        data: { imageDataUrl: imageDataUrl },
    }).done(function(response) {
        if ('error' in response && response.error === 'No face detected') {
            alert('No face detected');
        } 
        else if ('error' in response) {
            alert('Please Retake Picture');
        }
        else {
            window.location.href = "/show_results?result=" + encodeURIComponent(JSON.stringify(response));
        }
    });    
    

}


captureButton.addEventListener('click', captureImage);
