#! /bos/usr0/yubink/bin/ruby -I /bos/usr0/yubink/rubylib  -I .

require 'irmetrics'

results = nil
File.open(ARGV[0]) do |f|
  results = IRMetrics.load_all_results(f)
end

qrels = nil
File.open(ARGV[1]) do |f|
  qrels = IRMetrics.load_all_qrels(f)
end

for qnum, rels in qrels
  puts "#{qnum} #{IRMetrics.ap(rels,results[qnum]).round(4)}"
end
