"""
Automated job application submission with Browser-Use.

This script demonstrates:
- Complex form filling with multiple steps
- File upload (resume/CV)
- Cross-origin iframe handling
- Structured output with detailed summary
- Using Google's Gemini model for complex multi-step tasks

Example workflow:
1. Navigate to job application page
2. Fill out personal information fields
3. Upload resume
4. Complete optional/demographic fields
5. Submit application and confirm success
"""

import argparse
import asyncio
import json
import os

from dotenv import load_dotenv

from browser_use import Agent, Browser, Tools, ChatGoogle
from browser_use.tools.views import UploadFileAction

load_dotenv()


async def inject_start_button_and_wait(page):
    """
    Inject a two-step UI:
    1. 'FILL OUT APPLICATION' button
    2. Model selection dropdown + 'SUBMIT' button

    Uses JavaScript Promises to wait for user interactions.
    Returns the selected model name.
    """
    print("\n🌐 Browser opened. Waiting for you to click 'FILL OUT APPLICATION' button...")

    result = await page.evaluate("""() => {
        return new Promise((resolve) => {
            // Add CSS animation for entrance effect
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideUpFadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `;
            document.head.appendChild(style);

            // Step 1: Create initial "FILL OUT APPLICATION" button
            const initialButton = document.createElement('button');
            initialButton.id = 'start-application-btn';
            initialButton.innerHTML = 'FILL OUT APPLICATION';

            // Style the button (modern design with Inter font)
            initialButton.style.cssText = `
                position: fixed;
                top: 20px;
                left: 20px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                white-space: nowrap;
                height: 38px;
                padding: 0 32px;
                background: #fe750e;
                color: black;
                font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                border: 1px solid #fd8a3d;
                border-radius: 0;
                cursor: pointer;
                z-index: 2147483647;
                min-width: 180px;
                transition: all 0.2s ease;
                user-select: none;
                box-shadow: none;
                animation: slideUpFadeIn 0.6s ease-out;
            `;

            // Add hover effect
            initialButton.addEventListener('mouseenter', () => {
                initialButton.style.background = '#e66a0d';
                initialButton.style.boxShadow = '0 0 20px rgba(254, 117, 14, 0.4)';
            });

            initialButton.addEventListener('mouseleave', () => {
                initialButton.style.background = '#fe750e';
                initialButton.style.boxShadow = 'none';
            });

            // Click handler for initial button
            initialButton.addEventListener('click', () => {
                // Remove initial button
                initialButton.remove();

                // Step 2: Create model selection UI
                const container = document.createElement('div');
                container.id = 'model-selection-container';
                container.style.cssText = `
                    position: fixed;
                    top: 20px;
                    left: 20px;
                    display: flex;
                    gap: 8px;
                    z-index: 2147483647;
                `;

                // Create dropdown
                const dropdown = document.createElement('select');
                dropdown.id = 'model-dropdown';
                dropdown.style.cssText = `
                    height: 38px;
                    padding: 0 12px;
                    background: white;
                    color: black;
                    font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    border: 1px solid #fd8a3d;
                    border-radius: 0;
                    cursor: pointer;
                    outline: none;
                `;

                // Add options
                const options = [
                    { value: 'gemini-3-pro-preview', text: 'Google (gemini-3-pro-preview)' }
                ];

                options.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt.value;
                    option.textContent = opt.text;
                    option.selected = true;  // Only one option, so it's always selected
                    dropdown.appendChild(option);
                });

                // Create submit button
                const submitButton = document.createElement('button');
                submitButton.id = 'submit-model-btn';
                submitButton.innerHTML = 'SUBMIT';
                submitButton.style.cssText = `
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    white-space: nowrap;
                    height: 38px;
                    padding: 0 32px;
                    background: #fe750e;
                    color: black;
                    font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    border: 1px solid #fd8a3d;
                    border-radius: 0;
                    cursor: pointer;
                    min-width: 120px;
                    transition: all 0.2s ease;
                    user-select: none;
                    box-shadow: none;
                `;

                // Submit button hover effects
                submitButton.addEventListener('mouseenter', () => {
                    submitButton.style.background = '#e66a0d';
                    submitButton.style.boxShadow = '0 0 20px rgba(254, 117, 14, 0.4)';
                });

                submitButton.addEventListener('mouseleave', () => {
                    submitButton.style.background = '#fe750e';
                    submitButton.style.boxShadow = 'none';
                });

                // Submit button click handler
                submitButton.addEventListener('click', () => {
                    const selectedModel = dropdown.value;

                    // Visual feedback
                    submitButton.style.background = '#d55f0c';
                    submitButton.style.opacity = '0.5';
                    submitButton.style.pointerEvents = 'none';
                    submitButton.innerHTML = 'STARTING...';
                    dropdown.disabled = true;
                    dropdown.style.opacity = '0.5';

                    // Remove UI after short delay
                    setTimeout(() => {
                        container.remove();
                    }, 500);

                    // Resolve with selected model
                    resolve(selectedModel);
                });

                // Append elements to container
                container.appendChild(dropdown);
                container.appendChild(submitButton);

                // Append container to body
                document.body.appendChild(container);
            });

            // Append initial button to body
            document.body.appendChild(initialButton);
        });
    }""")

    print(f"✓ User selected model: {result}. Starting automated form filling...\n")
    return result


async def apply_to_job(applicant_info: dict, resume_path: str):
    """
    Apply to Rochester Regional Health job with provided information.

    Expected JSON format in applicant_info:
    {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "555-555-5555",
            "age": "21",
            "US_citizen": true,
            "sponsorship_needed": false,
            "postal_code": "12345",
            "country": "USA",
            "city": "Rochester",
            "address": "123 Main St",
            "gender": "Male",
            "race": "Asian",
            "Veteran_status": "Not a veteran",
            "disability_status": "No disability"
    }
    """

    # Use Gemini model for complex form filling tasks
    llm = ChatGoogle(model="gemini-3-pro-preview", thinking_budget=1)

    tools = Tools()

    # Flag to track if button has been clicked
    button_clicked = False

    @tools.action(description="Upload resume file")
    async def upload_resume(browser_session):
        params = UploadFileAction(path=resume_path, index=0)
        return "Ready to upload resume"

    @tools.action(description="Wait for user to click start button before proceeding")
    async def wait_for_start_button(browser_session):
        nonlocal button_clicked
        if not button_clicked:
            page = await browser_session.get_current_page()
            if page:
                await inject_start_button_and_wait(page)
                button_clicked = True
                return "User clicked start button - proceeding with form filling"
            else:
                return "Error: Could not get current page"
        return "Button already clicked, continuing"

    # Enable cross-origin iframe support for embedded application forms
    # Set headless=False so user can see the browser and click the button
    browser = Browser(cross_origin_iframes=True, headless=False)

    task = f"""
	- Your goal is to fill out and submit a job application form with the provided information.
	- Navigate to https://apply.appcast.io/jobs/50590620606/applyboard/apply/
	- FIRST: Use the wait_for_start_button action immediately after navigation. This will show a button for the user to click.
	- WAIT for the user to click the button before continuing with any form filling.
	- Scroll through the entire application and use extract_structured_data action to extract all the relevant information needed to fill out the job application form. use this information and return a structured output that can be used to fill out the entire form: {applicant_info}. Use the done action to finish the task. Fill out the job application form with the following information.
		- Before completing every step, refer to this information for accuracy. It is structured in a way to help you fill out the form and is the source of truth.
	- Follow these instructions carefully:
		- if anything pops up that blocks the form, close it out and continue filling out the form.
		- Do not skip any fields, even if they are optional. If you do not have the information, make your best guess based on the information provided.
		Fill out the form from top to bottom, never skip a field to come back to it later. When filling out a field, only focus on one field per step. For each of these steps, scroll to the related text. These are the steps:
			1) use input_text action to fill out the following:
				- "First name"
				- "Last name"
				- "Email"
				- "Phone number"
			2) use the upload_file_to_element action to fill out the following:
				- Resume upload field
			3) use input_text action to fill out the following:
				- "Postal code"
				- "Country"
				- "State"
				- "City"
				- "Address"
				- "Age"
			4) use click action to select the following options:
				- "Are you legally authorized to work in the country for which you are applying?"
				- "Will you now or in the future require sponsorship for employment visa status (e.g., H-1B visa status, etc.) to work legally for Rochester Regional Health?"
				- "Do you have, or are you in the process of obtaining, a professional license?"
					- SELECT NO FOR THIS FIELD
			5) use input_text action to fill out the following:
				- "What drew you to healthcare?"
			6) use click action to select the following options:
				- "How many years of experience do you have in a related role?"
				- "Gender"
				- "Race"
				- "Hispanic/Latino"
				- "Veteran status"
				- "Disability status"
			7) use input_text action to fill out the following:
				- "Today's date"
			8) CLICK THE SUBMIT BUTTON AND CHECK FOR A SUCCESS SCREEN. Once there is a success screen, complete your end task of writing final_result and outputting it.
	- Before you start, create a step-by-step plan to complete the entire task. make sure the delegate a step for each field to be filled out.
	*** IMPORTANT ***:
		- You are not done until you have filled out every field of the form.
		- When you have completed the entire form, press the submit button to submit the application and use the done action once you have confirmed that the application is submitted
		- PLACE AN EMPHASIS ON STEP 4, the click action. That section should be filled out.
		- At the end of the task, structure your final_result as 1) a human-readable summary of all detections and actions performed on the page with 2) a list with all questions encountered in the page. Do not say "see above." Include a fully written out, human-readable summary at the very end.
	"""

    # Make resume file available for upload
    available_file_paths = [resume_path]

    agent = Agent(
        task=task,
        llm=llm,
        demo_mode=True,
        browser=browser,
        tools=tools,
        available_file_paths=available_file_paths,
    )

    history = await agent.run()

    return history.final_result()


async def main(applicant_data_path: str, resume_path: str):
    # Verify files exist before starting
    if not os.path.exists(applicant_data_path):
        raise FileNotFoundError(f"Applicant data file not found: {applicant_data_path}")
    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Resume file not found: {resume_path}")

    # Load applicant information from JSON
    with open(applicant_data_path) as f:  # noqa: ASYNC230
        applicant_info = json.load(f)

    print(f"\n{'=' * 60}")
    print("Starting Job Application")
    print(f"{'=' * 60}")
    print(
        f"Applicant: {applicant_info.get('first_name')} {applicant_info.get('last_name')}"
    )
    print(f"Email: {applicant_info.get('email')}")
    print(f"Resume: {resume_path}")
    print(f"{'=' * 60}\n")

    # Submit the application
    result = await apply_to_job(applicant_info, resume_path=resume_path)

    # Display results
    print(f"\n{'=' * 60}")
    print("Application Result")
    print(f"{'=' * 60}")
    print(result)
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automated job application submission",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use included example data
  python main.py --resume example_resume.pdf

  # Use your own data
  python main.py --data my_info.json --resume my_resume.pdf
		""",
    )
    parser.add_argument(
        "--data",
        default="applicant_data.json",
        help="Path to applicant data JSON file (default: applicant_data.json)",
    )
    parser.add_argument(
        "--resume", required=True, help="Path to resume/CV file (PDF format)"
    )

    args = parser.parse_args()

    asyncio.run(main(args.data, args.resume))
