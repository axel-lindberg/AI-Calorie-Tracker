// Wires a mic button to the browser's Web Speech API so a meal can be
// dictated instead of typed. Feature-detected: browsers without support
// (e.g. Firefox) simply never show the mic button.
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

export function initSpeechInput({ textarea, micButton, statusEl }) {
  if (!SpeechRecognition) {
    return { stop() {} };
  }

  micButton.hidden = false;

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = true;
  recognition.interimResults = true;

  let listening = false;
  let baseText = '';
  let finalText = '';
  let errorMessage = '';

  function setListening(value) {
    listening = value;
    micButton.classList.toggle('is-listening', value);
    micButton.setAttribute('aria-pressed', String(value));
    micButton.title = value ? 'Stop dictation' : 'Dictate by voice';
    if (statusEl) statusEl.textContent = value ? 'Listening…' : errorMessage;
  }

  function updateTextarea(interim) {
    textarea.value = [baseText, (finalText + interim).trim()].filter(Boolean).join(' ');
  }

  micButton.addEventListener('click', () => {
    if (listening) {
      recognition.stop();
      return;
    }
    baseText = textarea.value.trim();
    finalText = '';
    errorMessage = '';
    try {
      recognition.start();
      setListening(true);
    } catch (err) {
      console.error('Could not start speech recognition', err);
    }
  });

  recognition.addEventListener('result', (event) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalText += `${transcript} `;
      } else {
        interim += transcript;
      }
    }
    updateTextarea(interim);
  });

  recognition.addEventListener('error', (event) => {
    console.error('Speech recognition error', event.error);
    errorMessage =
      event.error === 'not-allowed' || event.error === 'service-not-allowed'
        ? "Mic access denied — allow it in your browser's settings to dictate."
        : "Didn't catch that — try again.";
  });

  // 'end' always follows 'error', so this is where the final (possibly
  // error) status message actually gets displayed.
  recognition.addEventListener('end', () => {
    setListening(false);
  });

  return {
    stop() {
      if (listening) recognition.stop();
    },
  };
}
