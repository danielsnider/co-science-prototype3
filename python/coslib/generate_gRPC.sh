#!/usr/bin/env bash
rm *.pyc 
rm *pb2*
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. HDF5.proto
