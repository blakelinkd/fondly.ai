console.log('entering scroller.');
    document.addEventListener('DOMContentLoaded', function () {

        const modal = document.getElementById('modal');
        const closeBtn = document.getElementsByClassName('close-btn')[0];
      
        // Show the modal
        setTimeout(() => {
            console.log('modal timeout');
          modal.style.display = 'none';
        }, 4000); // Adjust the time as needed
      
        // Close the modal when the close button is clicked
        closeBtn.onclick = function () {
          modal.style.display = 'none';
        };
      
        // Close the modal when the user clicks outside the modal content
        modal.onclick = function (event) {
            modal.style.display = 'none';
        };


        // Double click for new image
        document.addEventListener('DOMContentLoaded', function () {
            const modal = document.getElementById('modal');
            const closeBtn = document.getElementsByClassName('close-btn')[0];
          
            // Show the modal
            setTimeout(() => {
              modal.style.display = 'block';
            }, 500); // Adjust the time as needed
          
            // Close the modal when the close button is clicked
            closeBtn.onclick = function () {
              modal.style.display = 'none';
            };
          
            // Close the modal when the user clicks outside the modal content
            window.onclick = function (event) {
              if (event.target == modal) {
                modal.style.display = 'none';
              }
            };
          });
        const imageDiv = document.querySelector('.image');
        imageDiv.addEventListener('dblclick', handleDoubleClick, false);
        function handleDoubleClick(evt) {
            evt.preventDefault();
    
            imageDiv.style.transition = 'transform 0.6s ease-in-out';
            imageDiv.style.transform = 'translateY(-100%)';
    
            fetch('/random-image')
                .then(response => response.json())
                .then(data => {
                    nextImage = data.image_url;
                    const newImage = new Image();
                    newImage.src = nextImage;
                    newImage.onload = () => {
                        imageDiv.style.transition = 'none';
                        imageDiv.style.transform = 'translateY(100%)';
                        imageDiv.style.backgroundImage = `url(${nextImage})`;
    
                        setTimeout(() => {
                            imageDiv.style.transition = 'transform 0.6s ease-in-out';
                            imageDiv.style.transform = 'translateY(0)';
                        }, 50);
                    };
                })
                .catch(error => console.error(error));
        }


        const likeHeart = document.getElementById('likeHeart');
        if (likeHeart) {
            likeHeart.addEventListener('touchstart', handleLikeTouchStart, false);
        }
        
        function handleLikeTouchStart(evt) {
            evt.preventDefault();
            likeHeart.style.color = 'gold';
            likeHeart.style.transform = 'scale(1.4)';
            
            setTimeout(() => {
                likeHeart.style.color = 'red';
                likeHeart.style.transform = 'scale(0)';
            }, 500);
            
            setTimeout(() => {
                likeHeart.style.transform = 'scale(1)';
            }, 1000);
            
            // Get the URL of the current image
            const imageDiv = document.querySelector('.image');
            const imageUrl = imageDiv.style.backgroundImage.slice(5, -2);
            
            // Send the image data to the like endpoint using an HTTP POST request
            fetch('/like', {
                method: 'POST',
                body: JSON.stringify({ image: imageUrl }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error(error));
        }
        
        
        
        const image = document.querySelector('.image');
        let nextImage = '';
        
        image.addEventListener('touchstart', handleTouchStart, false);
        image.addEventListener('touchmove', handleTouchMove, false);
        image.addEventListener('touchend', handleTouchEnd, false);
        
        let xDown = null;
        console.log('scroller');
        function handleTouchStart(evt) {
            xDown = evt.touches[0].clientY;
            console.log("touched");
        }
        
        function handleTouchMove(evt) {
            if (!xDown) {
                return;
            }
            
            const yUp = evt.touches[0].clientY;
            const yDiff = xDown - yUp;
            const multiplier = 3;
            
            image.style.transform = `translateY(${yDiff * -1 * multiplier}px)`; // Move the container quicker with the user's finger
        }
        
        function handleTouchEnd(evt) {
            if (!xDown) {
                return;
            }
            
            const yUp = evt.changedTouches[0].clientY;
            const yDiff = xDown - yUp;
            
            if (yDiff > 50) { // Increase swipe distance threshold
                // Swipe up detected
                image.style.transition = 'transform 0.6s ease-in-out'; // Adjust transition time
                image.style.transform = 'translateY(-100%)';
                
                fetch('/random-image')
                .then(response => response.json())
                .then(data => {
                    nextImage = data.image_url;
                    const newImage = new Image();
                    newImage.src = nextImage;
                    newImage.onload = () => {
                        image.style.transition = 'none';
                        image.style.transform = 'translateY(100%)'; // Move the container to the bottom
                        image.style.backgroundImage = `url(${nextImage})`;
                        
                        setTimeout(() => {
                            image.style.transition = 'transform 0.6s ease-in-out'; // Adjust transition time
                            image.style.transform = 'translateY(0)';
                        }, 50);
                    };
                })
                .catch(error => console.error(error));
            } else {
                // If swipe distance is less than the threshold, return the container to its initial position
                image.style.transition = 'transform 0.6s ease-in-out';
                image.style.transform = 'translateY(0)';
            }
            console.log(nextImage)

            xDown = null;
        }
    });