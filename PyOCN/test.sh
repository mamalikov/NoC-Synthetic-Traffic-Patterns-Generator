#!/bin/bash
python3 script/pymtl3-net sim mesh --ncols 16 --nrows 16 --injection-rate 40
python3 script/pymtl3-net sim mesh --ncols 16 --nrows 16 --pattern bit-complement --injection-rate 40
python3 script/pymtl3-net sim mesh --ncols 16 --nrows 16 --pattern bit-reverse --injection-rate 40
python3 script/pymtl3-net sim mesh --ncols 16 --nrows 16 --pattern bit-rotation --injection-rate 40
python3 script/pymtl3-net sim mesh --ncols 16 --nrows 16 --pattern shuffle --injection-rate 40
python3 script/pymtl3-net sim mesh --ncols 16 --nrows 16 --pattern transpose --injection-rate 40
python3 script/pymtl3-net sim mesh --ncols 16 --nrows 16 --pattern neighbor --injection-rate 40
python3 script/pymtl3-net sim mesh --ncols 16 --nrows 16 --pattern tornado --injection-rate 40
python3 script/pymtl3-net sim cmesh --ncols 16 --nrows 8 --injection-rate 40
python3 script/pymtl3-net sim cmesh --ncols 16 --nrows 8 --pattern bit-complement --injection-rate 40
python3 script/pymtl3-net sim cmesh --ncols 16 --nrows 8 --pattern bit-reverse --injection-rate 40
python3 script/pymtl3-net sim cmesh --ncols 16 --nrows 8 --pattern bit-rotation --injection-rate 40
python3 script/pymtl3-net sim cmesh --ncols 16 --nrows 8 --pattern shuffle --injection-rate 40
python3 script/pymtl3-net sim cmesh --ncols 16 --nrows 8 --pattern transpose --injection-rate 40
python3 script/pymtl3-net sim cmesh --ncols 16 --nrows 8 --pattern neighbor --injection-rate 40
python3 script/pymtl3-net sim cmesh --ncols 16 --nrows 8 --pattern tornado --injection-rate 40
python3 script/pymtl3-net sim bfly --nfly 8 --injection-rate 40
python3 script/pymtl3-net sim bfly --nfly 8 --pattern bit-complement --injection-rate 40
python3 script/pymtl3-net sim bfly --nfly 8 --pattern bit-reverse --injection-rate 40
python3 script/pymtl3-net sim bfly --nfly 8 --pattern bit-rotation --injection-rate 40
python3 script/pymtl3-net sim bfly --nfly 8 --pattern shuffle --injection-rate 40
python3 script/pymtl3-net sim bfly --nfly 8 --pattern transpose --injection-rate 40
python3 script/pymtl3-net sim bfly --nfly 8 --pattern neighbor --injection-rate 40
python3 script/pymtl3-net sim bfly --nfly 8 --pattern tornado --injection-rate 40