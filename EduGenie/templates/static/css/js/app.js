const task =
    document.getElementById("task");

const inputText =
    document.getElementById("inputText");

const submitBtn =
    document.getElementById("submitBtn");

const clearBtn =
    document.getElementById("clearBtn");

const copyBtn =
    document.getElementById("copyBtn");

const result =
    document.getElementById("result");

const status =
    document.getElementById("status");


const endpoints = {

    qa: "/qa",

    explain: "/explain",

    quiz: "/quiz",

    summarize: "/summarize",

    recommendations:
        "/learn/recommendations"

};


function setResultText(text) {

    result.className = "result";

    result.textContent = text;
}


function renderQuiz(data) {

    result.className = "result";


    result.innerHTML =
        data.questions.map(
            (question, index) => `

            <article
                class="quiz-question"
            >

                <h3>
                    ${index + 1}.
                    ${escapeHtml(
                        question.question
                    )}
                </h3>


                ${question.options.map(
                    (option, optionIndex) => `

                    <label class="option">

                        <input
                            type="radio"
                            name="q${index}"
                            value="${escapeAttr(
                                option
                            )}"
                        >

                        ${String.fromCharCode(
                            65 + optionIndex
                        )}.

                        ${escapeHtml(
                            option
                        )}

                    </label>

                `
                ).join("")}


                <button
                    class="secondary check-answer"
                    type="button"
                    data-index="${index}"
                >
                    Check answer
                </button>


                <p
                    id="feedback-${index}"
                ></p>

            </article>

        `
        ).join("");


    result
        .querySelectorAll(
            ".check-answer"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const index =
                        Number(
                            button.dataset.index
                        );


                    const selected =
                        result.querySelector(
                            `input[name="q${index}"]:checked`
                        );


                    const feedback =
                        document.getElementById(
                            `feedback-${index}`
                        );


                    if (!selected) {

                        feedback.textContent =
                            "Choose an option first.";

                        return;
                    }


                    const correct =
                        data.questions[
                            index
                        ].correct_answer;


                    if (
                        selected.value ===
                        correct
                    ) {

                        feedback.textContent =
                            "Correct!";

                    } else {

                        feedback.textContent =
                            `Not quite. Correct answer: ${correct}`;

                    }

                }
            );

        });
}


function renderPath(data) {

    result.className =
        "result";


    result.innerHTML = `

        <h3>
            ${escapeHtml(data.topic)}
        </h3>

    `;


    result.innerHTML +=
        data.steps.map(
            (step, index) => `

            <article
                class="path-step"
            >

                <strong>
                    ${index + 1}.
                    ${escapeHtml(
                        step.level
                    )}
                </strong>


                <p>

                    <strong>
                        Topics:
                    </strong>

                    ${
                        step.topics
                            .map(
                                escapeHtml
                            )
                            .join(", ")
                    }

                </p>


                <p>

                    <strong>
                        Suggested time:
                    </strong>

                    ${escapeHtml(
                        step.suggested_time
                    )}

                </p>


                <p>

                    <strong>
                        Resources:
                    </strong>

                    ${
                        step.resources
                            .map(
                                escapeHtml
                            )
                            .join(", ")
                        ||
                        "Use standard textbooks, documentation, or educational videos."
                    }

                </p>

            </article>

        `
        ).join("");
}


function escapeHtml(value) {

    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );
}


function escapeAttr(value) {

    return escapeHtml(value);
}


async function submit() {

    const text =
        inputText.value.trim();


    if (!text) {

        setResultText(
            "Please enter a question, topic, or passage."
        );

        result.classList.add(
            "error"
        );

        return;
    }


    submitBtn.disabled =
        true;

    status.textContent =
        "Generating...";


    result.className =
        "result";

    result.textContent =
        "EduGenie is thinking...";


    try {

        const response =
            await fetch(
                endpoints[task.value],
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        text: text
                    })

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Request failed."
            );

        }


        if (
            task.value ===
            "quiz"
        ) {

            renderQuiz(data);

        }

        else if (
            task.value ===
            "recommendations"
        ) {

            renderPath(data);

        }

        else {

            setResultText(
                data.result
            );

        }


        status.textContent =
            "Ready";

    }

    catch (error) {

        setResultText(
            error.message
        );

        result.classList.add(
            "error"
        );

        status.textContent =
            "Error";

    }

    finally {

        submitBtn.disabled =
            false;

    }
}


submitBtn.addEventListener(
    "click",
    submit
);


clearBtn.addEventListener(
    "click",
    () => {

        inputText.value = "";

        result.className =
            "result empty";

        result.textContent =
            "Your generated result will appear here.";

        status.textContent =
            "Ready";

    }
);


copyBtn.addEventListener(
    "click",
    async () => {

        await navigator.clipboard
            .writeText(
                result.innerText
            );


        const old =
            copyBtn.textContent;


        copyBtn.textContent =
            "Copied";


        setTimeout(
            () => {

                copyBtn.textContent =
                    old;

            },
            1200
        );

    }
);


task.addEventListener(
    "change",
    () => {

        const placeholders = {

            qa:
                "Example: What is the difference between RAM and ROM?",

            explain:
                "Example: Explain the Pythagoras theorem for a beginner.",

            quiz:
                "Paste a passage or topic here to generate 3 MCQs.",

            summarize:
                "Paste a long educational passage here.",

            recommendations:
                "Example: SQL"

        };


        inputText.placeholder =
            placeholders[
                task.value
            ];

    }
);