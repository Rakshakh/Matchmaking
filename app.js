const form = document.getElementById('onboarding-form');
const message = document.getElementById('message');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  message.className = '';

  if (!form.reportValidity()) {
    message.textContent = 'Please complete all required fields before submitting.';
    message.classList.add('error');
    return;
  }

  const formData = new FormData(form);
  const onboardingPayload = {
    fullName: formData.get('fullName'),
    email: formData.get('email'),
    instagram: formData.get('instagram'),
    linkedin: formData.get('linkedin'),
    presence: formData.getAll('presence'),
    extra: formData.get('extra') || '',
    consent: formData.get('consent') === 'on',
    submittedAt: new Date().toISOString()
  };

  localStorage.setItem('matchmakingOnboarding', JSON.stringify(onboardingPayload));

  message.textContent = 'Thanks! Your onboarding preferences have been saved on this device.';
  message.classList.add('success');
  form.reset();
});
