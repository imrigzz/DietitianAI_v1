let loader = document.getElementById('loaderid');

document.getElementById("change").addEventListener("click", myFunction);

function myFunction() {
    loader.classList.add('fondu-out')

    // When the div is shown:
    window.scrollTo(0, 0); // Scrolls to the top of the page
    loader.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
    console.log("running")
}





// Wait for the page to finish loading
window.addEventListener("load", function() {
    // Get the alert box element on the other page
    var alertBox =  document.getElementById("successMessage");
  
    // Show the alert box
    alertBox.style.display = "block";
  
    // Hide the alert box after 3 seconds (3000 milliseconds)
    setTimeout(function() {
      alertBox.style.display = "none";
    }, 5000);
  });

