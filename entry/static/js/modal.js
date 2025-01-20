// Open the modal for deleting a cart item in view_cartlist

function openRemoveModal(productId) {
    console.log('Opening modal for product ID:', productId); // Debugging
    const modal = document.getElementById('removeModal');
    if (modal) {
        modal.style.display = 'flex'; // Show the modal
    } else {
        console.error('Modal not found!');
    }
}

// Close the modal
function closeRemoveModal() {
    console.log('Closing modal'); // Debugging
    const modal = document.getElementById('removeModal');
    if (modal) {
        modal.style.display = 'none'; // Hide the modal
    } else {
        console.error('Modal not found!');
    }
}

// Confirms remove button after removing in the view_cartlist
document.getElementById('confirmRemoveButton').addEventListener('click', function () {
    if (currentCartId) {
        fetch(`/cartlist/remove/${currentCartId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (response.ok) {
                    // Remove the item from the cart UI (reload or dynamically remove)
                    alert('Item remved successfully');
                    loaction.reload(); // Reload the page to reflect the change
                } else {
                    alert('Failed to remove item. Please try again.');
                }
                closeRemoveModal();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occured. Please try again.');
                closeRemoveModal();
            });
    }
});
