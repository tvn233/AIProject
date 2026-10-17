# Checklist hoàn thiện trước nộp/bảo vệ

- [ ] Python >=3.11, tạo venv, `make setup && make demo` hoặc lệnh tương đương chạy từ clone mới.
- [ ] Có đủ 8 file corpus thật DOC0001–DOC0008, metadata doc_id/title/date/version/owner.
- [ ] `make test`: toàn bộ unit test pass, không mất test cũ.
- [ ] `make mcp-check`: server discover động; kiểm thử xác nhận NO/YES, verify, duplicate.
- [ ] `make eval`: đo hit@3 Dense/Hybrid, ghi bảng kết quả thật.
- [ ] `make eval-live`: đánh giá 12 câu × 2 chế độ; rà soát refusal/faithfulness bằng người thật.
- [ ] Ít nhất 3 phiên CLI chạy thật, 3 file `logs/*.jsonl` có timestamp/steps/tool args/results/USAGE.
- [ ] Rà soát quy đổi DOC0001 so với CTXH.md, kiểm tra trường hợp 14/15/16 điểm.
- [ ] Report Word 8–9 trang với kết quả thật, một failure case, sơ đồ kiến trúc.
- [ ] `ai-usage.md` khai báo trung thực, `.env`/DB cá nhân không lên Git.
- [ ] Git history có commit thật của từng người, hash trong report.
- [ ] Mỗi người biết giải thích và sửa trực tiếp file mình phụ trách.

## Câu hỏi bảo vệ

**Người 1:** Tại sao chunk 230 từ/overlap 30? E5 query/passsage prefix? Dense khác BM25? RRF là gì? Vì sao hit@3 không đồng nghĩa faithfulness?

**Người 2:** Agent Loop là gì? `MAX_STEPS` ngăn lỗi gì? JSON arguments hỏng thì sao? Timeout/retry hoạt động thế nào? LLM có được tự xác nhận đăng ký không?

**Người 3:** MCP khác gọi hàm Python trực tiếp? `stdio` stdout cần sạch vì sao? `tools/list` và `tools/call`? Read-after-write verify để làm gì? Khi nào báo đăng ký thành công?

**Cả nhóm:** demo 1 câu hỏi mới, 1 yêu cầu ghi, 1 no_answer, giải thích trace và token, thực hiện 1 thay đổi code nhỏ.
