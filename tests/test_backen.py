from textwrap import dedent
from typing import Literal

codes = {
    "python": {
        "types": ["py", "pypy"],
        "codes": [
            {
                "name": "fibo",
                "input": "30\n",
                "result": "832040\n",
                "status": "success",
                "code": dedent(
                    """
                from sys import setrecursionlimit
                setrecursionlimit(100000000)

                def fi(n=1):
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
                    while True:
                        pass
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
                "input": "30\n",
                "result": "832040",
                "status": "success",
                "code": dedent("""
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

    resp = httpx.post(
        "http://127.0.0.1:8000/api/v1/runner/" + code_type,
        json=dict(code=code, input=inp),
    )
    # print(resp.text)
    rst_resp = httpx.post(
        f"http://127.0.0.1:8000/api/v1/runner/get_result?task_id={resp.json()}"
    )
    try:
        return rst_resp.json()
    except json.decoder.JSONDecodeError:
        raise RuntimeError(rst_resp.text)


class Test:
    def test_py(self):
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
