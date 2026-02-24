const form = document.querySelector('#profile-form');
const matchList = document.querySelector('#match-list');
const emptyState = document.querySelector('#empty-state');

/** @type {Array<{name:string,age:number,minAge:number,maxAge:number,interests:string[]}>} */
const profiles = [
  {
    name: 'Morgan',
    age: 29,
    minAge: 24,
    maxAge: 35,
    interests: ['coffee', 'travel', 'running'],
  },
  {
    name: 'Avery',
    age: 27,
    minAge: 23,
    maxAge: 33,
    interests: ['gaming', 'coding', 'hiking'],
  },
  {
    name: 'Jordan',
    age: 31,
    minAge: 26,
    maxAge: 40,
    interests: ['music', 'hiking', 'movies'],
  },
];

function normalizeInterests(input) {
  return input
    .split(',')
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);
}

function calculateCompatibility(a, b) {
  let score = 0;

  const ageInRange = a.age >= b.minAge && a.age <= b.maxAge;
  const reverseAgeInRange = b.age >= a.minAge && b.age <= a.maxAge;
  if (ageInRange) score += 30;
  if (reverseAgeInRange) score += 30;

  const sharedInterests = a.interests.filter((interest) => b.interests.includes(interest));
  score += Math.min(sharedInterests.length * 20, 40);

  return {
    score,
    sharedInterests,
  };
}

function renderMatches(newProfile) {
  const matches = profiles
    .filter((profile) => profile.name !== newProfile.name)
    .map((profile) => {
      const compatibility = calculateCompatibility(newProfile, profile);
      return {
        profile,
        ...compatibility,
      };
    })
    .filter((match) => match.score > 0)
    .sort((a, b) => b.score - a.score);

  matchList.innerHTML = '';

  if (matches.length === 0) {
    emptyState.textContent = 'No strong matches yet. Add more profiles and try again.';
    emptyState.hidden = false;
    return;
  }

  emptyState.hidden = true;

  matches.forEach((match) => {
    const li = document.createElement('li');
    li.className = 'match-item';

    const shared =
      match.sharedInterests.length > 0
        ? `Shared interests: ${match.sharedInterests.join(', ')}`
        : 'No shared interests listed';

    li.innerHTML = `
      <strong>${match.profile.name} (${match.profile.age}) — ${match.score}% match</strong>
      <span class="muted">${shared}</span>
    `;

    matchList.appendChild(li);
  });
}

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const name = document.querySelector('#name').value.trim();
  const age = Number(document.querySelector('#age').value);
  const minAge = Number(document.querySelector('#preferred-min-age').value);
  const maxAge = Number(document.querySelector('#preferred-max-age').value);
  const interests = normalizeInterests(document.querySelector('#interests').value);

  if (!name || minAge > maxAge) {
    emptyState.textContent = 'Please provide valid profile values.';
    emptyState.hidden = false;
    return;
  }

  const profile = { name, age, minAge, maxAge, interests };
  profiles.push(profile);
  renderMatches(profile);

  form.reset();
  document.querySelector('#preferred-min-age').value = '22';
  document.querySelector('#preferred-max-age').value = '35';
});
