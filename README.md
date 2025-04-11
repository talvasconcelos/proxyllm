# ProxyLLM - <small>[LNbits](https://github.com/lnbits/lnbits) extension</small>

<small>For more about LNbits extensions, check out the [official documentation](https://github.com/lnbits/lnbits/wiki/LNbits-Extensions)</small>

## 🧠 Monetize your AI with Bitcoin

ProxyLLM is an LNbits extension that lets AI service providers rent access to their language models (LLMs) — securely and instantly — using the Lightning Network. Whether you're running a local LLM or proxying OpenAI, you can now get paid per prompt, per minute, or per token, and control exactly how others access your model.

Users browse a marketplace of available LLMs, pay upfront for access, and receive an endpoint + API key to use the service — without ever seeing the provider's credentials.

---

## 💼 Features

- Register LLM endpoints (local, OpenAI, Groq, etc.)
- Set your pricing: per request, per token, or per minute
- Users prepay with sats for access (secure via LNbits wallet)
- Extension acts as a proxy (credentials never exposed)
- Public agent listing with metadata (model, specialization, price)
- Track usage and earnings
- LNbits takes a service fee per job (optional)

---

## 🧪 Usage

### 🔹 For LLM Providers (Clients)

1. Install the **ProxyLLM** extension
2. Click **“Register Agent”**
3. Provide:
   - Agent name, endpoint, description
   - Model info (e.g. gpt-3.5)
   - Price and unit type
4. Choose a wallet to receive payments
5. Your agent is now live on the **ProxyLLM Marketplace**

### 🔹 For Users

1. Browse available AI agents
2. Choose one and click **"Access Agent"**
3. Prepay for usage (e.g., 10 requests for 500 sats)
4. Get your:
   - Unique proxy URL
   - API Key
5. Send prompts using your software, CLI, or app

---

## 🔒 Example API Request

```http
POST /api/v1/agents/proxy/<agent_id>
Headers:
  X-Api-Key: <your_prepaid_key>
Body:
  {
    "prompt": "Translate to Spanish: Hello, world!",
    "model": "gpt-3.5-turbo"
  }
