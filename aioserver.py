import json
import asyncio
import functools
import multiprocessing
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor

MANAGER = multiprocessing.Manager()

async_queue = asyncio.Queue(maxsize=50)
process_queue = MANAGER.Queue()

class ModelService:
    def __init__(self, test_fn):
        self.test_fn = test_fn

    def process_samples(self, samples):
        return self.test_fn(samples)

    def serve(self):
        while True:
            x, v, lock = process_queue.get(block=True)
            try:
                res = self.process_samples(x)
            except:
                res = None

            if res is None or type(res) is not list or len(res) != len(x):
                res = [None] * len(x)
            v.set(res)
            lock.release()

async def web_handle(request):
    web_input = await request.json()
   # web_input['image'] = base64_cv2(web_input['image'])

    future = asyncio.get_event_loop().create_future()
    try:
        async_queue.put_nowait((web_input, future))
    except asyncio.queues.QueueFull:
        return web.json_response({'code': 202, 'msg': 'busy', 'data': {}}, status=202)
    await future
    
    msg = future.result()
    if msg is None:
        msg = {'code': 201, 'msg': 'unknown error', 'data': {}}
        status = 201
    else:
        status = 200
    return web.Response(body=json.dumps(msg, ensure_ascii=False), status=status, content_type='application/json')

def wait_results(lock, shared_value, web_inputs: list):
    lock.acquire()
    process_queue.put((web_inputs, shared_value, lock))

    lock.acquire()
    lock.release()

    return shared_value.get()

async def async_queue_handle(executor: ThreadPoolExecutor):
    lock = MANAGER.Lock()
    shared_value = MANAGER.Value(bytes, b'')
    loop = asyncio.get_event_loop()
    print('async queue handler starts...')
    while True:
        web_input, future   = await async_queue.get()
        web_inputs, futures = [web_input], [future]
        while async_queue.qsize() > 0:
            web_input, future = async_queue.get_nowait()
            web_inputs.append(web_input)
            futures.append(future)

        print('async queue handler put {} items into process queue'.format(len(web_inputs)))

        res = await loop.run_in_executor(executor, functools.partial(wait_results, lock, shared_value, web_inputs))
        for r, f in zip(res, futures):
            try:
                f.set_result(r)
            except asyncio.base_futures.InvalidStateError:
                pass

async def _run_app(app, host, port=None):
    runner = web.AppRunner(app, handle_signals=True)
    await runner.setup()
    try:
        site = web.TCPSite(runner, host, port)
        await site.start()
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()

async def async_service(host, port, route_path):
    app = web.Application()
    app.add_routes([web.post(route_path, web_handle)])

    coroutine1 = async_queue_handle(ThreadPoolExecutor())
    coroutine2 = _run_app(app, host=host, port=port)

    await asyncio.gather(coroutine1, coroutine2)

def start_inference_service(custom_func, host, port, route_path):
    def process_fn():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_service(host=host, port=port, route_path=route_path))

    p  = multiprocessing.Process(target=process_fn)
    ms = ModelService(custom_func)
    p.start()
    ms.serve()
    p.join()
