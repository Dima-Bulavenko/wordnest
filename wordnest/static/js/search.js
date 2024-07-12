const textElement = document.getElementById("word");
const runButton = document.getElementById("translate_word");
const source_language = document.querySelector('[name="source_language"]');
const target_language = document.querySelector('[name="target_language"]');

var translationTippy = tippy(textElement, {
    maxWidth: "none",
    allowHTML: true,
    arrow: false,
    interactive: true,
    placement: "bottom-start",
    trigger: "manual",
    content: "Loading...",
    onCreate(instance) {
        instance._isFetching = false;
    },
    onShow(instance) {
        translateText(instance);
        instance.popper.style.minWidth = `${instance.reference.offsetWidth}px`;
    },
    onHidden(instance) {
        instance.setContent("Loading...");
    },
});

/**
 * Shows or hides the add button based on the input value.
 *
 * @param {Event} event - The event object from the input event.
 */
function showRunButton(event) {
    const inputValue = event.target.value;
    if (inputValue.length > 0) {
        runButton.style.display = "block";
    } else {
        runButton.style.display = "none";
    }
}

/**
 * Creates a div element containing translations.
 *
 * @param {Array} translations - An array of translation objects.
 * @returns {HTMLElement} A div element with id 'search_results'.
 */
function createSearchResults(translations) {
    const searchResults = document.createElement("div");
    searchResults.id = "search_results";

    for (let translation of translations) {
        if (!translation.text) continue;

        let resultElement = document.createElement("div");
        resultElement.className = "search_result";
        resultElement.innerText = translation.text;
        resultElement.addEventListener("click", addWordToDictionary);
        searchResults.appendChild(resultElement);
    }

    if (!searchResults.children.length) {
        searchResults.innerText = "No results found";
    }
    return searchResults;
}

function addWordToDictionary(event) {
    if (translationTippy._isFetching) return;

    const word = textElement.value;
    const translation = event.target.innerText;
    const sourceLang = source_language.value;
    const targetLang = target_language.value;
    translationTippy._isFetching = true;
    fetch("/dictionary/add-word/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: JSON.stringify({
            word: word,
            translation: translation,
            source_language: sourceLang,
            target_language: targetLang,
        }),
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        translationTippy.hide();
    })
    .catch((error) => {
        const messageTippy = tippy(document.body, {
            trigger: "manual",
            allowHTML: true,
            arrow: false,
            content: () => {
                let message = "An error occurred. Please reload the page and try again."; 
                let element = document.createElement("div");
                element.classList.add("add_word_error")
                element.innerText = message;
                return element; 
            },
        })
        messageTippy.show();
        setTimeout(() => messageTippy.hide(), 3000);
    })
    .finally(() => {
        translationTippy._isFetching = false;
    });
}

/**
 * Sends a POST request to the server to translate the text entered by the user.
 *
 * @param {Object} instance - Must be a Tippy object.
 */
function translateText(instance) {
    if (instance._isFetching) return;

    const text = textElement.value.trim();
    const sourceLang = document.querySelector('[name="source_language"]').value;
    const targetLang = document.querySelector('[name="target_language"]').value;
    instance._isFetching = true;
    fetch("/translate/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: JSON.stringify({
            body: text,
            from_language: sourceLang,
            to_language: targetLang,
        }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            let popover = createSearchResults(data.translations);
            instance.setContent(popover);
        })
        .catch((error) => {
            instance.setContent("An error occurred. Please try again later.");
        })
        .finally(() => {
            instance._isFetching = false;
        });
}

document.addEventListener("DOMContentLoaded", function () {
    textElement.addEventListener("input", showRunButton);
    textElement.addEventListener("input", () => {
        if (translationTippy.state.isVisible) {
            translationTippy.hide();
        }
    });
    textElement.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            translationTippy.show();
        }
    });
    runButton.addEventListener("click", () => translationTippy.show());
});

module.exports = { showRunButton, createSearchResults };
