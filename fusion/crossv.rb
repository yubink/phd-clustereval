#! /bos/usr0/yubink/bin/ruby -I /bos/usr0/yubink/rubylib  -I .
# inputs:
#   query list; queries to train, queries to test?
#   auto-1 
#   assume, rank list files + .Qeval contains trec eval results. in same dir

require 'optparse'
require 'slidefuse'
require 'irmetrics'


$options = {}

op = OptionParser.new do |opts|
  opts.banner = """Usage ./crossv.rb [options] [rank list files] ...
  Creates a fused result set of a given rank list of files"""

#  opts.on("-w", "--window NUM", Integer, "Window size param for SlideFuse") do |x|
#    $options[:window] = x
#  end
#
#  opts.on("-o", "--output DIR", "Output directory") do |f|
#    $options[:outdir] = f
#  end

  opts.on("-q", "--qrels FILE", "File containing qrels") do |f|
    $options[:qrels] = f
  end
end

op.parse!


qrels = nil
File.open($options[:qrels]) do |f|
  qrels = IRMetrics.load_all_qrels(f)
end

$stderr.puts "read qrels"

#list_weights = Hash.new
#File.open($options[:weightf]) do |f|
#  for line in f
#    map, runname = line.split
#    map_vals[runname] = map.to_f    
#  end
#end


all_lists = []
for rankfile in ARGV
  name = File.basename(rankfile)

  map_vals = Hash.new
  File.open(rankfile + ".Qeval") do |f|
    for line in f
      if line.start_with?("map ")
        metric, qnum, val = line.split
        if qnum != "all"
          map_vals[qnum] = val.to_f
        end
      end
    end
  end

  results = nil
  File.open(rankfile) do |f|
    results = IRMetrics.load_all_results(f)
  end

  data = ListData.new(name, map_vals, results)
  all_lists << data
end

$stderr.puts "read results and qevals"

all_qnums = qrels.keys
for qnum, rels in qrels
  $stderr.puts "#{qnum}"
  window_scores = Hash.new
  for window in [1, 2, 5, 10, 20]
    train_qnums = all_qnums - [qnum]
    fuser = SlideFuseMap.new(window)
    fuser.train(all_lists, train_qnums, qrels)
    train_fused = fuser.fuse(all_lists, train_qnums)
    score = IRMetrics.map(qrels, train_fused, train_qnums)

    fused = fuser.fuse(all_lists, [qnum])
    window_scores[window] = [score, fused[qnum]]
    $stderr.puts "#{window} #{score}"
  end

  sorted_windows = window_scores.to_a.sort {|x,y| y[1][0] <=> x[1][0]}
  top_w = sorted_windows[0]
  $stderr.puts "Best window #{qnum}: #{top_w[0]}"
  $stderr.puts "   AP was #{top_w[1][0]}"

  #puts top_w[1][1][0...1000]
  puts top_w[1][1]
end


