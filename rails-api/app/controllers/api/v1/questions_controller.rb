module Api
  module V1
    class QuestionsController < ApplicationController
      def create
        if params[:store_id].blank? || params[:question].blank?
          render json: { error: "store_id and question are required" }, status: :bad_request
          return
        end
      
        result = PythonAiService.ask(params[:store_id], params[:question])
      
        render json: result
      end
    end
  end
end
