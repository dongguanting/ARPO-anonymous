import sys
import os
sys.path.append(os.getcwd())
import asyncio
import argparse


infer_mode_help = """Inference mode selection
[default]       :    Basic behavior similar to the original search tool, uses summarization and continuously appends to the assistant content.
[completion]    :    Builds on [default] by adding feedback for exceeding the Python or search call limits, and for repeated search queries.
[completion_sds]:    Builds on [completion] by using a simple deep search engine.
"""

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Asynchronous inference engine")
    parser.add_argument(
        '--infer_mode', type=str, required=True, 
        choices=[
            'completion',
            'completion_sds',
            'default',
        ],
        default='default',
        help=infer_mode_help,
    )
    parser.add_argument("--turns", type=int, nargs='+', default=[1, 2, 3],
                        help='Number of inference turns to run')
    
    vllm_group = parser.add_argument_group("VLLM Configuration")
    vllm_group.add_argument("--endpoints", type=str, nargs='+', required=True,
                            help="List of VLLM endpoints")
    vllm_group.add_argument("--model_path", type=str, required=True,
                            help="Model path for tokenizer loading")
    vllm_group.add_argument("--api_keys", type=str, nargs='+', default=None,
                            help="List of API keys corresponding to endpoints")
    vllm_group.add_argument("--default_model", type=str, default="Qwen2.5-7B-Instruct",
                            help="Default model name to use")
    
    generation_group = parser.add_argument_group("Generation Parameters")
    generation_group.add_argument("--temperature", type=float, default=0,
                                  help="Temperature for generation")
    generation_group.add_argument("--max_tokens", type=int, default=4096,
                                  help="Maximum number of new tokens to generate")
    generation_group.add_argument("--top_p", type=float, default=0.8,
                                  help="Top-p sampling cutoff")
    generation_group.add_argument("--top_k", type=int, default=20,
                                  help="Top-k sampling cutoff")
    generation_group.add_argument("--min_p", type=float, default=0.0,
                                  help="Minimum probability threshold")
    generation_group.add_argument("--repetition_penalty", type=float, default=1.1,
                                  help="Repetition penalty factor")
    generation_group.add_argument("--include_stop_str_in_output", type=bool, default=True,
                                  help="Whether to include stop strings in output")

    inference_group = parser.add_argument_group("Inference Configuration")
    inference_group.add_argument("--max_concurrent_requests", type=int, default=50,
                                 help="Maximum number of concurrent samples to process")
    inference_group.add_argument("--dataset_name", type=str, nargs='+', default=['math'],
                                 help="List of dataset names (separated by space)")
    inference_group.add_argument("--output_path", type=str,
                                 help="Root directory for saving results. Dataset results are saved at /root/dataset_name/dataset_name_output_i.json")
    inference_group.add_argument("--prompt_type", type=str, default='code_search',
                                 help="Prompt type (code_search, search, math, base)")
    inference_group.add_argument("--counts", type=int, default=100,
                                 help="Number of samples to process")
    inference_group.add_argument("--data_path", type=str, default=None,
                                 help="Custom data path. Datasets are expected at /root_path/dataset_name/test.jsonl")
    inference_group.add_argument("--max_python_times", type=int, default=5,
                                 help="Maximum number of Python tool invocations")
    inference_group.add_argument("--max_search_times", type=int, default=3,
                                 help="Maximum number of search tool invocations")
    inference_group.add_argument("--sample_timeout", type=int, default=120,
                                 help="Timeout in seconds for processing a single sample")

    tools_group = parser.add_argument_group("Tool Configuration")
    tools_group.add_argument("--conda_path", type=str",
                             help="Path to Conda installation")
    tools_group.add_argument("--conda_env", type=str,
                             help="Conda environment name")
    tools_group.add_argument("--python_max_concurrent", type=int, default=32,
                             help="Maximum concurrency for Python executor")
    tools_group.add_argument("--bing_api_key", type=str, required=True,
                             help="Bing Search API key")
    tools_group.add_argument("--bing_zone", type=str, default="serp_api1",
                             help="Bing search region")
    tools_group.add_argument("--search_max_results", type=int, default=10,
                             help="Maximum number of search results")
    tools_group.add_argument("--search_result_length", type=int, default=1000,
                             help="Maximum length of each search result")
    tools_group.add_argument("--bing_requests_per_second", type=float, default=2.0,
                             help="Maximum Bing requests per second")
    tools_group.add_argument("--bing_max_retries", type=int, default=3,
                             help="Maximum number of Bing retries")
    tools_group.add_argument("--bing_retry_delay", type=float, default=1.0,
                             help="Delay between Bing retries (in seconds)")
    tools_group.add_argument("--summ_model_urls", type=str, nargs='+', default=["http://localhost:8004/v1"],
                             help="Local summarization LLM API endpoints")
    tools_group.add_argument("--summ_model_name", type=str, default="Qwen2.5-72B-Instruct",
                             help="Name of local summarization LLM")
    tools_group.add_argument("--summ_model_path", type=str",
                             help="Path to local summarization LLM for tokenizer")
    tools_group.add_argument("--search_cache_file", type=str, default="search_cache.db",
                             help="Cache file for search results")
    tools_group.add_argument("--url_cache_file", type=str, default="search_url_cache.db",
                             help="Cache file for web pages")  
    return parser.parse_args()


def get_inference_instance():
    args = parse_arguments()
    print(vars(args))
    infer_mode = args.infer_mode
    if infer_mode == 'chat':
        from src.inference_engine_cn import AsyncInferenceChat as AsyncInfer
    elif infer_mode == 'chat_sds':
        from src.inference_engine_cn import AsyncInferenceChatSDS as AsyncInfer
    elif infer_mode == 'completion':
        from src.inference_engine_cn import AsyncInferenceCompletion as AsyncInfer
    elif infer_mode == 'completion_sds':
        from src.inference_engine_cn import AsyncInferenceCompletionSDS as AsyncInfer
    elif infer_mode == 'default':
        from src.inference_engine_cn import AsyncInference as AsyncInfer
    else:
        raise ValueError('Unknown inference mode: ', infer_mode)
   
    inference = AsyncInfer(args)
    return inference

async def main():
    inference = get_inference_instance()
    await inference.run()
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
