class PythonAiService
  include HTTParty
  base_uri "http://127.0.0.1:8000"

  def self.ask(store_id, question)
    response = post(
      "/ask",
      headers: { "Content-Type" => "application/json" },
      body: {
        store_id: store_id,
        question: question
      }.to_json
    )

    JSON.parse(response.body)
  rescue StandardError
    {
      "answer" => "AI service is currently unavailable.",
      "confidence" => "low"
    }
  end
end
