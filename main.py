import io
import json
import base64
import requests
from typing import Dict, Union
import os
import openai
import re
from augmatrix.block_service.service_runner import ServerManager, ServiceRunner
from openai import OpenAI

class GPTRedactTask(ServiceRunner):
    def __init__(self, logger: object) -> None:
        """
        Initialize GPT Redact Task object.

        Parameters:
        logger (object): A logger object to log messages and errors.
        """
        self.logger = logger
        super().__init__(structure_json_path='./structure.json')

    def run(self, inputs, properties, credentials):
        """
        Perform masking using OpenAI model.

        Parameters:
        inputs (Dict): A dictionary object containing the input data.
        properties (Dict): Additional properties for task execution.
        credentials (Dict): Credentials required for OpenAI API.

        Returns:
        Dict: Prediction results.
        """
        openai.organization = credentials.get("OPENAI_ORG", os.getenv("OPENAI_ORG", None))
        openai.api_key = credentials.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", None))

        if openai.organization is None or openai.api_key is None:
            raise ValueError("OpenAI credentials are not provided")

        input_text = inputs.text.replace("\n", "\n\n")

        prompt = f"""
            Instructions         
                1. Do not write code. Directly perform the task on the provided 'text'.
                2. Use "__START__" and "__END__" to indicate the start and end of the 'final output'.
                3. If a value does not exist, set it as an empty string ("").
                4. Format the output strictly as shown in the example below. Do not add any extra text or characters outside the specified JSON structure.

            Input 'text':
            ----------
            ```
                {input_text}
            ```
            ----------

            Your final output should match the following format exactly:
            ----------
            __START__
            ```{json.dumps({"masked_data": ""})}```
            __END__
            ----------

            Example as shown below

            System Prompt: Mask sensitive details such as 'Policy Number' and 'Phone Number' with '*'.

             Input 'text':
            ----------
            ```
                The policy number is 123456789 and the phone number is 555-555-5555.
            ```
            ----------

            Your final output should match the following format exactly:
            ----------
            __START__
            ```{json.dumps({"masked_data": "The policy number is ********* and the phone number is ************."})}```
            __END__
            ----------

        """
        client = OpenAI()
        
        # Use the updated method to create completions with the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"Mask sensitive details such as ```{', '.join(properties['label_text_list'])}``` with '*'.",
            }, {
                "role": "user",
                "content": prompt
            }],
        )

        if not response.choices:
            raise ValueError("No response from OpenAI API.")
        
        response_text = response.choices[0].message.content.strip()
        start_text = r"__START__\s*```(json)?"
        end_text = "```\s*__END__"
        match = re.search(f"{start_text}(?P<output>(.|\n)+){end_text}", response_text, re.DOTALL)

        if match:
            # Extracting the value from the named group 'extraction'
            extraction = match.group('output').strip()
        else:
            raise ValueError("Failed to extract JSON from response.")

        result = None
        try:
            result = {"predict": json.loads(extraction)}
        except json.decoder.JSONDecodeError as e:
            print(e)

        return result


if __name__ == "__main__":
    ServerManager(GPTRedactTask(logger=None)).start(
        host="localhost",
        port=8083,
        # Assuming TLS/SSL is not a requirement for this migration example.
        # If secure communication is required, uncomment and provide paths to the certificate and private key.
        # private_key="certificates/private.pem",
        # cert_key="certificates/cert.pem"
    )