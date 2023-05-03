#!/usr/bin/env perl

use strict;
use warnings;
use feature qw(say);

use List::Util qw(max);

sub get_options {
   my $_ = shift;
   my ( $option, %options );

   {
      if ( m/\G.*?\s*parser[.]add_option(\s*'(?<d>-\w)'\s*,\s*'--(?<d>\w*(?:(?>-\w+)+))',\s*/g ) {
         $option = join ' ', @{$-{d}};
         redo;
      }

      if ( m/\G.*?(?<h>help\s*=(?:\s*'(?<h>.+?)'\s*)+)/g ) {
         $options{$option}{d} = $+{h};

         {
            if ( m/\G\s+'(?<h>.+?)'\s*/g ) {
               $options{$option}{d} .= $+{h};
               redo;
            }
         }
         redo;
      }

      if ( m/\G.*?\s+metavar\s*=\s*'(?<v>.+?)'\s*,/g ) {
         $options{v} = $+{v};
         redo;
      }

   }

   return %options;
}

sub output_options_doc {
   my $options = shift;

   say '> Mandatory arguments to long options are mandatory for short options too.'
   foreach $option (keys %options) {
      printf '> **%s**\n', $opts;
      printf '>> %s\n', $options{$option};
   }
}

sub get_synopsis {
   my %options = shift
   my $synopsis = map '[ ' . ( $_ =~ s/ /|/ ) . ( $options{v} // '' =~ s/(.+)/**$1**/ ) . ']', keys %options;

   printf '> **ima** %s **QUERY** [..QUERY]\n', $synopsis
}

print <<"HEADING"
# NAME

> ima - Image searcher and downloader

# SYNOPSIS

HEADING

output_synopsis
output_options_doc

print <<"FOOTER"
AUTHORS
> $AUTHORS

REPORTING BUGS
> $BUGS

COPYRIGHT

FOOTER
