import numpy as np
import tritonclient.http as httpclient

client = httpclient.InferenceServerClient(url="triton.llm-inference.svc:8000")

inputs = []
data = np.array([[1,2,3,4]], dtype=np.int32)
inp = httpclient.InferInput("input_ids", data.shape, "INT32")
inp.set_data_from_numpy(data)
inputs.append(inp)

outputs = [httpclient.InferRequestedOutput("output_ids")]

response = client.infer(model_name="llama3", inputs=inputs, outputs=outputs)
print(response.as_numpy("output_ids"))
