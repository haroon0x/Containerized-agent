#!/bin/bash
if pgrep Xtigervnc && nc -z localhost 5901; then
  exit 0
else
  exit 1
fi