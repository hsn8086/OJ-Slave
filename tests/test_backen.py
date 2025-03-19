from textwrap import dedent
from typing import Literal

codes = {
    "python": {
        "types": ["py", "pypy","codon"],
        "codes": [
            {
                "name": "fibo",
                "input": "35\n",
                "result": "9227465\n",
                "status": "success",
                "code": dedent(
                    """
                def fi(n: int = 1):
                    if n in [1,2]:
                        return 1
                    else:
                        return fi(n-1)+fi(n-2)

                print(fi(int(input())))"""
                ),
            },
            {
                "name": "TLE",
                "input": "",
                "result": "",
                "status": "timeout",
                "code": dedent(
                    """
                    a=0
                    while True:
                        a+=1
                    print(a)
                    """
                ),
            },
            {
                "name": "MLE",
                "input": "",
                "result": "",
                "status": "memory_limit_exceeded",
                "code": dedent("""
                    list(range(100000000))
                    """),
            },
        ],
    },
    "c": {
        "types": ["gcc", "gpp"],
        "codes": [
            {
                "name": "fibo",
                "input": "35\n",
                "result": "9227465",
                "status": "success",
                "code": dedent("""
                    #pragma GCC optimize(2)
                    #include <stdio.h>
                    int fibonacci(int n) {
                        if(n == 1 || n == 2) {
                            return 1;
                        }
                        return fibonacci(n-1) + fibonacci(n-2);
                    }

                    int main() {
                        int n;
                        scanf("%d",&n);
                        printf("%d", fibonacci(n));
                        return 0;
                    }
                """),
            },
            {
                "name": "TLE",
                "input": "",
                "result": "",
                "status": "timeout",
                "code": dedent("""
                    int main() {
                        while (1) {}
                        return 0;
                    }
                """),
            },
            {
                "name": "MLE",
                "input": "",
                "result": "",
                "status": "memory_limit_exceeded",
                "code": dedent("""
                    #include <stdio.h>
                    #include <stdlib.h>

                    int main() {
                        size_t size = 512 * 1024 * 1024;
                        char *memory = (char *)malloc(size);

                        for (size_t i = 0; i < size; i++) {
                            memory[i] = (char)(i % 256);
                        }
                        return 0;
                    }                 
                """),
            },
            {
                "name": "CE",
                "input": "",
                "result": "",
                "status": "compile_error",
                "code": dedent("""
                    int main() {
                        return 0;
                """),
            },
        ],
    },
}


def req(code_type: Literal["py", "pypy"], code: str, inp: str):
    import httpx
    import json
    # url="192.168.49.2:30000"
    url="127.0.0.1:8000"
    resp = httpx.post(
        f"http://{url}/api/v1/runner/" + code_type,
        json=dict(code=code, input=inp),
    )
    # print(resp.text)
    rst_resp = httpx.get(
        f"http://{url}/api/v1/runner/get_result?task_id={resp.json()}",timeout=10
    )
    try:
        return rst_resp.json()
    except json.decoder.JSONDecodeError:
        raise RuntimeError(rst_resp.text)


class Test:
    def test_code(self):
        for name, group_d in codes.items():
            print(f'running group: "{name}".')
            for code_type in group_d["types"]:
                print(f'- running type: "{code_type}".')
                for d in group_d["codes"]:
                    print(f'| - running code: "{d["name"]}"')
                    try:
                        rst_d = req(code=d["code"], inp=d["input"], code_type=code_type)
                        print("  | - ", rst_d)
                    except RuntimeError as e:
                        print("  | - error: ", e)
                    if d["result"]:
                        assert rst_d["output"] == d["result"]
                    if d["status"]:
                        assert rst_d["type"] == d["status"]

    # def test_press(self):
    #     import httpx
        
    #     ids = []
    #     for _ in range(100):
    #         for name, group_d in codes.items():
    #             print(f'running group: "{name}".')
    #             for code_type in group_d["types"]:
    #                 print(f'- running type: "{code_type}".')
    #                 for d in group_d["codes"]:
    #                     print(f'| - running code: "{d["name"]}"')
    #                     resp = httpx.post(
    #                         "http://127.0.0.1:8000/api/v1/runner/" + code_type,
    #                         json=dict(code=d["code"], input=d["input"]),
    #                     )
    #                     ids.append(resp.json())
    #         # print("rst:")
    #         # for id_ in ids:
    #         #     rst_resp = httpx.post(
    #         #         f"http://127.0.0.1:8000/api/v1/runner/get_result?task_id={resp.json()}"
    #         #     )
    #         #     print("- ", rst_resp.json())
