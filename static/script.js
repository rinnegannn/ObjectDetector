document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('photo-inputer');
    const uploadButton = document.getElementById('photo-input');
    const preview = document.getElementById('preview');
    const description = document.getElementById('description');
    const scanBtn = document.getElementById('scan-btn');
    const readBtn = document.getElementById('read-btn');
   
    // Store detected objects
    let detectedObjects = [];
   
    // Display preview of selected image
    fileInput.addEventListener('change', function(e) {
      if (this.files && this.files[0]) {
        const reader = new FileReader();
       
        reader.onload = function(e) {
          preview.src = e.target.result;
          description.textContent = 'Image selected. Click SCAN to analyze.';
          scanBtn.disabled = false;
        };
       
        reader.readAsDataURL(this.files[0]);
      }
    });
   
    // Handle the upload/scan process
    uploadButton.addEventListener('click', function(e) {
      e.preventDefault();
      fileInput.click();
    });
   
    scanBtn.addEventListener('click', function() {
      if (!fileInput.files || !fileInput.files[0]) {
        description.textContent = 'Please select an image first.';
        return;
      }
     
      // Change button state and description
      scanBtn.disabled = true;
      scanBtn.querySelector('.status-indicator').classList.add('scanning');
      description.textContent = 'Scanning image...';
     
      // Create FormData and append the file
      const formData = new FormData();
      formData.append('file', fileInput.files[0]);
     
      // Send the image to the server for processing
      fetch('/upload', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log('Received data:', data);
       
        // Update the image with processed version (with bounding boxes)
        if (data.image) {
          preview.src = 'data:image/jpeg;base64,' + data.image;
        }
       
        // Store detected objects
        detectedObjects = data.objects || [];
       
        // Update UI
        description.textContent = detectedObjects.length > 0
          ? `Detected ${detectedObjects.length} object(s): ${detectedObjects.join(', ')}`
          : 'No objects detected.';
       
        scanBtn.querySelector('.status-indicator').classList.remove('scanning');
        scanBtn.disabled = false;
        readBtn.disabled = detectedObjects.length === 0;
      })
      .catch(error => {
        console.error('Error:', error);
        description.textContent = 'Error processing image. Please try again.';
        scanBtn.querySelector('.status-indicator').classList.remove('scanning');
        scanBtn.disabled = false;
      });
    });
   
    // Handle read aloud functionality
    readBtn.addEventListener('click', function() {
      if (detectedObjects.length === 0) {
        return;
      }
     
      fetch('/read-aloud', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ objects: detectedObjects })
      })
      .then(response => response.json())
      .then(data => {
        console.log('Read aloud:', data.message);
      })
      .catch(error => {
        console.error('Error:', error);
      });
    });
  });