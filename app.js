const form = document.getElementById('matchForm');
const resultEl = document.getElementById('result');

function selectedInterests() {
  const checked = Array.from(document.querySelectorAll('input[name="interest"]:checked'));
  return checked.map((el) => el.value);
}

function enforceInterestLimit() {
  const boxes = Array.from(document.querySelectorAll('input[name="interest"]'));
  boxes.forEach((box) => {
    box.addEventListener('change', () => {
      const chosen = selectedInterests();
      const disabled = chosen.length >= 3;
      boxes.forEach((candidate) => {
        if (!candidate.checked) {
          candidate.disabled = disabled;
        }
      });
    });
  });
}

function renderMatch(match) {
  resultEl.innerHTML = `
    <h2>Match result</h2>
    <div class="result-card">
      <strong>${match.name}</strong>, ${match.age} — ${match.city}<br />
      Intent: ${match.intent}<br />
      Shared fit score: <strong>${match.score}%</strong><br />
      Interests: ${match.interests.join(', ')}
    </div>
  `;
}

function renderError(message) {
  resultEl.innerHTML = `
    <h2>Match result</h2>
    <p class="error">${message}</p>
  `;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const age = document.getElementById('age').value;
  const intent = document.getElementById('intent').value;
  const interests = selectedInterests();

  const query = new URLSearchParams({
    age,
    intent,
    interests: interests.join(',')
  });

  try {
    const response = await fetch(`/api/match?${query.toString()}`);
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || 'Unable to find match');
    }

    renderMatch(payload.match);
  } catch (error) {
    renderError(error.message);
  }
});

enforceInterestLimit();
