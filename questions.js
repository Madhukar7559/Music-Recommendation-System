// JavaScript file to store answers in a list

// Array to store answers
const answers = [];

// Function to save answers
function saveAnswer() {
  // Get selected answer
  const selectedAnswer = document.querySelector('input[name]:checked').value;
  // Add answer to answers list
  answers.push(selectedAnswer);
  // Redirect to the next page or result page
  if (location.pathname.includes('page1.html')) {
    location.href = 'page2.html';
  } else {
    location.href = 'result.html';
  }
}